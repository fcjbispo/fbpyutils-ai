import os
import uuid
import asyncio
import logging
import time
import glob
from typing import Dict, Any, Optional, List, Union
from uuid import uuid4
import threading
import pickle
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from browser_use.agent.service import Agent
from browser_use.browser.browser import Browser, BrowserConfig
from browser_use.browser.context import (
    BrowserContextConfig,
    BrowserContextWindowSize,
)
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.language_models.base import BaseLanguageModel

from src.utils.agent_state import AgentState
from src.utils import utils
from src.agent.custom_agent import CustomAgent
from src.browser.custom_browser import CustomBrowser
from src.agent.custom_prompts import CustomSystemPrompt, CustomAgentMessagePrompt
from src.browser.custom_context import BrowserContextConfig, CustomBrowserContext
from src.controller.custom_controller import CustomController
from src.utils.deep_research import deep_research

# Configure logging
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

@dataclass
class BrowserUITask:
    """Class to track asynchronous task information"""
    id: str
    task_type: str
    future: asyncio.Future
    start_time: float
    stop_requested: bool = False
    result_path: Optional[str] = None

class BrowserUIAgent:
    """Class to implement browser automation functionalities from webui.py as a reusable component"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize BrowserUIAgent with configuration settings
        
        Args:
            config: Dictionary containing configuration settings for the agent
        """
        # Validate and store configuration
        self._validate_config(config)
        self.config = config
        
        # Create random output directory for this instance if not specified
        self.output_dir = config.get('output_dir', os.path.join('./tmp', f'browser_ui_agent_{uuid4()}'))
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Setup directory structure for outputs
        self.recordings_dir = os.path.join(self.output_dir, 'recordings')
        self.traces_dir = os.path.join(self.output_dir, 'traces')
        self.agent_history_dir = os.path.join(self.output_dir, 'agent_history')
        self.research_dir = os.path.join(self.output_dir, 'research')
        
        os.makedirs(self.recordings_dir, exist_ok=True)
        os.makedirs(self.traces_dir, exist_ok=True)
        os.makedirs(self.agent_history_dir, exist_ok=True)
        os.makedirs(self.research_dir, exist_ok=True)
        
        # Setup global state
        self._browser = None
        self._browser_context = None
        self._agent = None
        self._agent_state = AgentState()
        
        # Initialize LLM
        self._llm = self._get_llm_from_config()
        
        # Task tracking
        self._tasks: Dict[str, BrowserUITask] = {}
        self._task_lock = threading.Lock()
        self._executor = ThreadPoolExecutor(max_workers=10)
    
    def _validate_config(self, config: Dict[str, Any]) -> None:
        """
        Validate configuration dictionary
        
        Args:
            config: Configuration dictionary to validate
        
        Raises:
            ValueError: If required configuration is missing or invalid
        """
        required_fields = [
            'agent_type',
            'headless', 
            'window_w', 
            'window_h'
        ]
        
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Required configuration field '{field}' is missing")
        
        # Validate agent_type
        if config.get('agent_type') not in ['org', 'custom']:
            raise ValueError(f"Invalid agent_type: {config.get('agent_type')}. Must be 'org' or 'custom'")
    
    def _get_llm_from_config(self) -> BaseLanguageModel:
        """
        Get LLM based on configuration
        
        Returns:
            Configured LLM instance
        """
        llm_provider = self.config.get('llm_provider', 'openai')
        
        if self.config.get('llm_instance'):
            return self.config.get('llm_instance')
        
        # Configure LLM parameters from config
        llm_params = {
            'provider': llm_provider,
            'model_name': self.config.get('llm_model_name', 'gpt-4o'),
            'temperature': self.config.get('llm_temperature', 0.0),
            'base_url': self.config.get('llm_base_url', ''),
            'api_key': self.config.get('llm_api_key', ''),
        }
        
        # Add num_ctx for ollama models
        if llm_provider == 'ollama':
            llm_params['num_ctx'] = self.config.get('llm_num_ctx', 32000)
            
        return utils.get_llm_model(**llm_params)
    
    def _resolve_sensitive_env_variables(self, text: str) -> str:
        """
        Replace environment variable placeholders ($SENSITIVE_*) with their values.
        Only replaces variables that start with SENSITIVE_.
        
        Args:
            text: Text potentially containing environment variable placeholders
            
        Returns:
            Text with environment variables resolved
        """
        if not text:
            return text
            
        import re
        
        # Find all $SENSITIVE_* patterns
        env_vars = re.findall(r'\$SENSITIVE_[A-Za-z0-9_]*', text)
        
        result = text
        for var in env_vars:
            # Remove the $ prefix to get the actual environment variable name
            env_name = var[1:]  # removes the $
            env_value = os.getenv(env_name)
            if env_value is not None:
                # Replace $SENSITIVE_VAR_NAME with its value
                result = result.replace(var, env_value)
            
        return result
    
    async def _setup_browser(self):
        """Initialize or reuse browser instance based on configuration"""
        use_own_browser = self.config.get('use_own_browser', False)
        headless = self.config.get('headless', True)
        disable_security = self.config.get('disable_security', True)
        window_w = self.config.get('window_w', 1280)
        window_h = self.config.get('window_h', 1100)
        
        # Set up browser arguments
        extra_chromium_args = [f"--window-size={window_w},{window_h}"]
        cdp_url = None  # CDP support is disabled in this implementation
        chrome_path = None
        
        # Initialize browser if needed
        if self._browser is None:
            if self.config.get('agent_type') == 'org':
                self._browser = Browser(
                    config=BrowserConfig(
                        headless=headless,
                        cdp_url=cdp_url,
                        disable_security=disable_security,
                        chrome_instance_path=chrome_path,
                        extra_chromium_args=extra_chromium_args,
                    )
                )
            else:  # custom agent
                self._browser = CustomBrowser(
                    config=BrowserConfig(
                        headless=headless,
                        disable_security=disable_security,
                        cdp_url=cdp_url,
                        chrome_instance_path=chrome_path,
                        extra_chromium_args=extra_chromium_args,
                    )
                )
        
        # Initialize browser context if needed
        if self._browser_context is None:
            self._browser_context = await self._browser.new_context(
                config=BrowserContextConfig(
                    trace_path=self.traces_dir if self.traces_dir else None,
                    save_recording_path=self.recordings_dir if self.config.get('enable_recording', True) else None,
                    no_viewport=False,
                    browser_window_size=BrowserContextWindowSize(
                        width=window_w, height=window_h
                    ),
                )
            )
    
    async def _cleanup_browser(self):
        """Clean up browser resources if keep_browser_open is False"""
        if not self.config.get('keep_browser_open', False):
            if self._browser_context:
                await self._browser_context.close()
                self._browser_context = None
            
            if self._browser:
                await self._browser.close()
                self._browser = None
    
    async def _run_org_agent(self, task: str) -> Dict[str, Any]:
        """
        Run the org agent to perform a browser task
        
        Args:
            task: Task description to execute
            
        Returns:
            Dictionary containing execution results
        """
        try:
            self._agent_state.clear_stop()
            
            await self._setup_browser()
            
            # Create and run agent
            if self._agent is None:
                self._agent = Agent(
                    task=task,
                    llm=self._llm,
                    use_vision=self.config.get('use_vision', True),
                    browser=self._browser,
                    browser_context=self._browser_context,
                    max_actions_per_step=self.config.get('max_actions_per_step', 10),
                    tool_calling_method=self.config.get('tool_calling_method', 'auto')
                )
            
            history = await self._agent.run(max_steps=self.config.get('max_steps', 100))
            
            # Save history
            history_file = os.path.join(self.agent_history_dir, f"{self._agent.agent_id}.json")
            self._agent.save_history(history_file)
            
            # Get results
            final_result = history.final_result()
            errors = history.errors()
            model_actions = history.model_actions()
            model_thoughts = history.model_thoughts()
            
            # Get latest trace file
            latest_traces = utils.get_latest_files(self.traces_dir)
            trace_file = latest_traces.get('.zip')
            
            # Get latest recording file
            latest_videos = []
            if self.config.get('enable_recording', True):
                new_videos = glob.glob(os.path.join(self.recordings_dir, "*.[mM][pP]4")) + \
                            glob.glob(os.path.join(self.recordings_dir, "*.[wW][eE][bB][mM]"))
                if new_videos:
                    latest_videos = sorted(new_videos, key=os.path.getctime, reverse=True)
            
            return {
                'final_result': final_result,
                'errors': errors,
                'model_actions': model_actions,
                'model_thoughts': model_thoughts,
                'latest_video': latest_videos[0] if latest_videos else None,
                'trace_file': trace_file,
                'history_file': history_file,
                'task_id': self._agent.agent_id
            }
            
        except Exception as e:
            import traceback
            error_str = str(e) + "\n" + traceback.format_exc()
            return {
                'final_result': '',
                'errors': error_str,
                'model_actions': '',
                'model_thoughts': '',
                'latest_video': None,
                'trace_file': None,
                'history_file': None,
                'task_id': str(uuid4())
            }
        finally:
            self._agent = None
            await self._cleanup_browser()
    
    async def _run_custom_agent(self, task: str, add_infos: str = '') -> Dict[str, Any]:
        """
        Run the custom agent to perform a browser task
        
        Args:
            task: Task description to execute
            add_infos: Additional information for the agent
            
        Returns:
            Dictionary containing execution results
        """
        try:
            self._agent_state.clear_stop()
            
            await self._setup_browser()
            
            controller = CustomController()
            
            # Create and run agent
            if self._agent is None:
                self._agent = CustomAgent(
                    task=task,
                    add_infos=add_infos,
                    use_vision=self.config.get('use_vision', True),
                    llm=self._llm,
                    browser=self._browser,
                    browser_context=self._browser_context,
                    controller=controller,
                    system_prompt_class=CustomSystemPrompt,
                    agent_prompt_class=CustomAgentMessagePrompt,
                    max_actions_per_step=self.config.get('max_actions_per_step', 10),
                    tool_calling_method=self.config.get('tool_calling_method', 'auto')
                )
            
            history = await self._agent.run(max_steps=self.config.get('max_steps', 100))
            
            # Save history
            history_file = os.path.join(self.agent_history_dir, f"{self._agent.agent_id}.json")
            self._agent.save_history(history_file)
            
            # Get results
            final_result = history.final_result()
            errors = history.errors()
            model_actions = history.model_actions()
            model_thoughts = history.model_thoughts()
            
            # Get latest trace file
            latest_traces = utils.get_latest_files(self.traces_dir)
            trace_file = latest_traces.get('.zip')
            
            # Get latest recording file
            latest_videos = []
            if self.config.get('enable_recording', True):
                new_videos = glob.glob(os.path.join(self.recordings_dir, "*.[mM][pP]4")) + \
                            glob.glob(os.path.join(self.recordings_dir, "*.[wW][eE][bB][mM]"))
                if new_videos:
                    latest_videos = sorted(new_videos, key=os.path.getctime, reverse=True)
            
            return {
                'final_result': final_result,
                'errors': errors,
                'model_actions': model_actions,
                'model_thoughts': model_thoughts,
                'latest_video': latest_videos[0] if latest_videos else None,
                'trace_file': trace_file,
                'history_file': history_file,
                'task_id': self._agent.agent_id
            }
            
        except Exception as e:
            import traceback
            error_str = str(e) + "\n" + traceback.format_exc()
            return {
                'final_result': '',
                'errors': error_str,
                'model_actions': '',
                'model_thoughts': '',
                'latest_video': None,
                'trace_file': None,
                'history_file': None,
                'task_id': str(uuid4())
            }
        finally:
            self._agent = None
            await self._cleanup_browser()
    
    async def _execute_deep_research(self, research_task: str, max_search_iterations: int = 3, max_query_num: int = 1) -> Dict[str, Any]:
        """
        Execute deep research on a given topic
        
        Args:
            research_task: Research topic to investigate
            max_search_iterations: Maximum number of search iterations
            max_query_num: Maximum queries per iteration
            
        Returns:
            Dictionary containing research results
        """
        try:
            self._agent_state.clear_stop()
            
            # Create unique research directory for this task
            task_dir = os.path.join(self.research_dir, str(uuid4()))
            
            # Execute deep research
            research_kwargs = {
                'save_dir': task_dir,
                'max_search_iterations': max_search_iterations,
                'max_query_num': max_query_num,
                'use_vision': self.config.get('use_vision', True),
                'headless': self.config.get('headless', True),
                'use_own_browser': self.config.get('use_own_browser', False),
                'chrome_cdp': None  # CDP not supported
            }
            
            markdown_content, file_path = await deep_research(
                research_task, 
                self._llm, 
                self._agent_state, 
                **research_kwargs
            )
            
            return {
                'markdown_content': markdown_content,
                'file_path': file_path,
                'task_dir': task_dir
            }
            
        except Exception as e:
            import traceback
            error_str = str(e) + "\n" + traceback.format_exc()
            return {
                'markdown_content': f"Error during deep research: {error_str}",
                'file_path': None,
                'task_dir': None,
                'error': error_str
            }
    
    def stop_task(self, task_id: str) -> bool:
        """
        Request to stop a running task
        
        Args:
            task_id: The ID of the task to stop
            
        Returns:
            True if task was found and stop was requested, False otherwise
        """
        with self._task_lock:
            if task_id in self._tasks:
                task = self._tasks[task_id]
                task.stop_requested = True
                
                # Request agent to stop
                if task.task_type in ['agent', 'research']:
                    self._agent_state.request_stop()
                
                return True
            
            return False
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get status information about a task
        
        Args:
            task_id: The ID of the task to check
            
        Returns:
            Dictionary with task status information
        """
        with self._task_lock:
            if task_id in self._tasks:
                task = self._tasks[task_id]
                future = task.future
                
                status = {
                    'id': task_id,
                    'task_type': task.task_type,
                    'start_time': task.start_time,
                    'elapsed_time': time.time() - task.start_time,
                    'stop_requested': task.stop_requested,
                    'status': 'running'
                }
                
                if future.done():
                    status['status'] = 'completed' if not future.exception() else 'failed'
                    if task.result_path:
                        status['result_path'] = task.result_path
                    
                    # If task is complete and we have a result, we can clean it up
                    if status['status'] == 'completed':
                        try:
                            result = future.result()
                            status['result'] = result
                        except Exception as e:
                            status['error'] = str(e)
                            status['status'] = 'failed'
                
                return status
            
            return {'id': task_id, 'status': 'not_found'}
    
    def list_tasks(self) -> List[Dict[str, Any]]:
        """
        List all tasks and their statuses
        
        Returns:
            List of task status dictionaries
        """
        tasks = []
        with self._task_lock:
            for task_id in self._tasks:
                tasks.append(self.get_task_status(task_id))
        
        return tasks
    
    def cleanup_completed_tasks(self) -> int:
        """
        Clean up completed tasks from the task list
        
        Returns:
            Number of tasks cleaned up
        """
        tasks_to_remove = []
        
        with self._task_lock:
            for task_id, task in self._tasks.items():
                if task.future.done():
                    tasks_to_remove.append(task_id)
            
            for task_id in tasks_to_remove:
                del self._tasks[task_id]
        
        return len(tasks_to_remove)
    
    def save_config(self, file_path: str) -> bool:
        """
        Save current configuration to a file
        
        Args:
            file_path: Path to save the configuration file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            
            # Don't save the LLM instance in the config
            save_config = self.config.copy()
            if 'llm_instance' in save_config:
                del save_config['llm_instance']
            
            with open(file_path, 'wb') as f:
                pickle.dump(save_config, f)
            
            return True
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return False
    
    @classmethod
    def load_config(cls, file_path: str) -> Dict[str, Any]:
        """
        Load configuration from a file
        
        Args:
            file_path: Path to load the configuration file from
            
        Returns:
            Dictionary containing the loaded configuration
        """
        try:
            with open(file_path, 'rb') as f:
                config = pickle.load(f)
            
            return config
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return {}
    
    def _register_task(self, task_type: str, future: asyncio.Future) -> str:
        """
        Register a new task in the task list
        
        Args:
            task_type: Type of task ('agent' or 'research')
            future: Future object for the task
            
        Returns:
            Task ID
        """
        task_id = str(uuid4())
        
        with self._task_lock:
            self._tasks[task_id] = BrowserUITask(
                id=task_id,
                task_type=task_type,
                future=future,
                start_time=time.time()
            )
        
        return task_id
    
    def _task_complete_callback(self, task_id: str, future: asyncio.Future) -> None:
        """
        Callback when a task completes
        
        Args:
            task_id: ID of the completed task
            future: Future object of the task
        """
        try:
            # If task was successful, store result path
            if not future.exception():
                result = future.result()
                
                with self._task_lock:
                    if task_id in self._tasks:
                        if isinstance(result, dict):
                            # Store relevant path information
                            if result.get('history_file'):
                                self._tasks[task_id].result_path = result.get('history_file')
                            elif result.get('file_path'):
                                self._tasks[task_id].result_path = result.get('file_path')
        except Exception as e:
            logger.error(f"Error in task completion callback: {e}")
    
    def _run_agent_in_event_loop(self, task: str, add_infos: str = '') -> Dict[str, Any]:
        """
        Run agent in a new event loop (for use in thread pool)
        
        Args:
            task: Task description
            add_infos: Additional information
            
        Returns:
            Dictionary with agent execution results
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        agent_type = self.config.get('agent_type', 'custom')
        
        try:
            if agent_type == 'org':
                return loop.run_until_complete(self._run_org_agent(task))
            else:
                return loop.run_until_complete(self._run_custom_agent(task, add_infos))
        finally:
            loop.close()
    
    def _run_research_in_event_loop(self, research_task: str, max_search_iterations: int, max_query_num: int) -> Dict[str, Any]:
        """
        Run deep research in a new event loop (for use in thread pool)
        
        Args:
            research_task: Research task description
            max_search_iterations: Maximum search iterations
            max_query_num: Maximum queries per iteration
            
        Returns:
            Dictionary with research results
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            return loop.run_until_complete(
                self._execute_deep_research(research_task, max_search_iterations, max_query_num)
            )
        finally:
            loop.close()
    
    # Synchronous API methods
    
    def run_agent(self, task: str, add_infos: str = '') -> Dict[str, Any]:
        """
        Run browser agent synchronously
        
        Args:
            task: Task description to execute
            add_infos: Additional information for the agent
            
        Returns:
            Dictionary containing execution results
        """
        # Resolve sensitive environment variables
        task = self._resolve_sensitive_env_variables(task)
        
        # Run the agent
        agent_type = self.config.get('agent_type', 'custom')
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            if agent_type == 'org':
                return loop.run_until_complete(self._run_org_agent(task))
            else:
                return loop.run_until_complete(self._run_custom_agent(task, add_infos))
        finally:
            loop.close()
    
    def run_deep_research(self, research_task: str, max_search_iterations: int = 3, max_query_num: int = 1) -> Dict[str, Any]:
        """
        Execute deep research synchronously
        
        Args:
            research_task: Research topic to investigate
            max_search_iterations: Maximum number of search iterations
            max_query_num: Maximum queries per iteration
            
        Returns:
            Dictionary containing research results
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            return loop.run_until_complete(
                self._execute_deep_research(research_task, max_search_iterations, max_query_num)
            )
        finally:
            loop.close()
    
    # Asynchronous API methods
    
    def run_agent_async(self, task: str, add_infos: str = '') -> str:
        """
        Run browser agent asynchronously
        
        Args:
            task: Task description to execute
            add_infos: Additional information for the agent
            
        Returns:
            Task ID that can be used to check status or stop the task
        """
        # Resolve sensitive environment variables
        task = self._resolve_sensitive_env_variables(task)
        
        # Submit task to executor
        future = self._executor.submit(self._run_agent_in_event_loop, task, add_infos)
        
        # Register task
        task_id = self._register_task('agent', future)
        
        # Add completion callback
        future.add_done_callback(lambda f: self._task_complete_callback(task_id, f))
        
        return task_id
    
    def run_deep_research_async(self, research_task: str, max_search_iterations: int = 3, max_query_num: int = 1) -> str:
        """
        Execute deep research asynchronously
        
        Args:
            research_task: Research topic to investigate
            max_search_iterations: Maximum number of search iterations
            max_query_num: Maximum queries per iteration
            
        Returns:
            Task ID that can be used to check status or stop the task
        """
        # Submit task to executor
        future = self._executor.submit(
            self._run_research_in_event_loop, 
            research_task, 
            max_search_iterations, 
            max_query_num
        )
        
        # Register task
        task_id = self._register_task('research', future)
        
        # Add completion callback
        future.add_done_callback(lambda f: self._task_complete_callback(task_id, f))
        
        return task_id
    
    def get_result(self, task_id: str, wait: bool = True, timeout: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """
        Get the result of an asynchronous task
        
        Args:
            task_id: Task ID
            wait: If True, wait for the task to complete
            timeout: Maximum time to wait for result (in seconds)
            
        Returns:
            Dictionary with task result or None if not available
        """
        with self._task_lock:
            if task_id not in self._tasks:
                return None
            
            task = self._tasks[task_id]
            future = task.future
        
        if wait:
            try:
                # Wait for the future to complete with optional timeout
                result = future.result(timeout=timeout) if timeout else future.result()
                return result
            except TimeoutError:
                return {'status': 'running', 'message': 'Operation still in progress'}
            except Exception as e:
                return {'status': 'error', 'message': str(e)}
        else:
            # Return immediately if future is done
            if future.done():
                try:
                    return future.result()
                except Exception as e:
                    return {'status': 'error', 'message': str(e)}
            else:
                return {'status': 'running', 'message': 'Operation still in progress'}


# Example usage
if __name__ == "__main__":
    # Example configuration
    config = {
        'agent_type': 'custom',           # Use custom agent implementation
        'headless': True,                 # Run headless browser
        'window_w': 1280,                 # Browser window width
        'window_h': 800,                  # Browser window height
        'llm_provider': 'openai',         # LLM provider
        'llm_model_name': 'gpt-4o',       # LLM model name
        'llm_temperature': 0.2,           # LLM temperature
        'max_steps': 20,                  # Maximum agent steps
        'use_vision': True,               # Use vision capabilities
        'max_actions_per_step': 5,        # Maximum actions per step
        'enable_recording': True,         # Enable browser recording
        'output_dir': './tmp/browser_ui_agent_example'  # Output directory
    }
    
    # Create the agent
    agent = BrowserUIAgent(config)
    
    # Example 1: Synchronous use
    print("Running synchronous agent...")
    result = agent.run_agent("Go to bbc.com and give me the titles of the top 3 news stories")
    print(f"Result: {result['final_result']}")
    
    # Example 2: Asynchronous use
    print("\nRunning asynchronous agent...")
    task_id = agent.run_agent_async("Go to weather.com and check the weather forecast for New York")
    
    # Check status
    while True:
        status = agent.get_task_status(task_id)
        print(f"Task status: {status['status']}")
        
        if status['status'] != 'running':
            break
            
        time.sleep(2)
    
    # Get final result
    result = agent.get_result(task_id)
    print(f"Result: {result['final_result']}")
    
    # Example 3: Deep research
    print("\nRunning deep research...")
    research_id = agent.run_deep_research_async(
        "Provide a comprehensive overview of large language models and their applications in healthcare", 
        max_search_iterations=2
    )
    
    # Check status periodically
    for _ in range(5):
        status = agent.get_task_status(research_id)
        print(f"Research status: {status['status']}")
        time.sleep(5)
        
        # Option to stop research early
        if _ == 2:
            print("Stopping research early...")
            agent.stop_task(research_id)
    
    # Wait for result
    research_result = agent.get_result(research_id)
    if research_result and 'markdown_content' in research_result:
        print(f"Research report first 100 chars: {research_result['markdown_content'][:100]}...")
        print(f"Report saved at: {research_result.get('file_path')}")
    
    # Clean up tasks
    cleaned = agent.cleanup_completed_tasks()
    print(f"Cleaned up {cleaned} completed tasks")