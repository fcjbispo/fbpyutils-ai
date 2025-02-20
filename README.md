# Projeto de IA em Python - Documentação

## 1. Introdução
Este projeto implementa uma plataforma de IA capaz de executar diversas tarefas automática, incluindo:
- Pesquisa na internet
- Extração de conteúdo web
- Manipulação de planilhas Excel
- Leitura e criação de arquivos em vários formatos (JSON, CSV, HTML)
- Análise e descrição de imagens
- Criação de imagens a partir de prompts
- Interação com bancos de dados SQL
- Integração com APIs remotas

## 2. Funcionalidades Principais

### 2.1 Pesquisa na Internet
Implementamos uma ferramenta de busca genérica e uma ferramenta específica para o SearXNG.

A classe `SearchTool` em `fbpyutils_ai/tools/search.py` fornece uma interface abstrata para ferramentas de busca. A classe `SearXNGTool` implementa essa interface para realizar buscas usando a API REST do SearXNG.

Para usar a ferramenta de busca SearXNG, você precisa inicializar a classe `SearXNGTool` com a URL base do seu serviço SearXNG:

```python
from fbpyutils_ai.tools.search import SearXNGTool

searxng_tool = SearXNGTool(base_url="https://searxng.instance")
results = searxng_tool.search("OpenAI", params={"category_general": "1"})
print(results)
```

Os parâmetros de busca podem ser passados para o método `search` como um dicionário. Consulte a documentação da API do SearXNG para obter a lista completa de parâmetros suportados.

### 2.2 Extração de Conteúdo Web
Extrai dados e informações de páginas web usando técnicas de scraping.

### 2.3 Manipulação de Planilhas Excel
Lê, analisa e manipula dados em planilhas Excel para suportar tarefas como cálculos, filtros e exportação de dados.

### 2.4 Análise de Imagens
Processa imagens para identificar características visuais e gerar descrições textuais.

### 2.5 Criação de Imagens
Gera imagens a partir de prompts textuais usando modelos de geração de conteúdo.

### 2.6 Interação com Bancos de Dados
Conecta-se a bancos de dados SQL para executar consultas e atualizações de dados.

### 2.7 Integração com APIs
Interage com serviços web via HTTP requests, permitindo a execução de operações como POST, GET, PUT e DELETE.

## 3. Como Usar o Projeto

### 3.1 Setup do Ambiente
Para instalar as dependências, execute:
```bash
pip install -r requirements.txt
```

O arquivo `requirements.txt` contém todas as bibliotecas necessárias para executar o projeto.

### 3.2 Exemplos de Uso

#### 3.2.1 Pesquisa na Internet
```python
# Exemplo de uso
results = search_webpage("OpenAI", "sua_chave_api")
print(results)
```

#### 3.2.2 Manipulação de Planilhas Excel
```python
# Exemplo de uso
data = read_excel("exemplo.xlsx")
print(data)
```

#### 3.2.3 Criação de Imagens
```python
# Exemplo de uso
image_url = generate_image("Um gato tocando piano")
print(image_url)
```

## 4. Documentação Completa
Para mais detalhes sobre cada funcionalidade e como integrá-las, consulte os documentos fornecidos:
- [AGENTS.md](https://github.com/yourusername/yourproject/blob/main/docs/AGENTS.md)
- [TOOLS.md](https://github.com/yourusername/yourproject/blob/main/docs/TOOLS.md)

## 5. Contribuição
Sinta-se livre para contribuir com o projeto! Se você tiver dúvidas ou sugestões, contate-nos no repositório ou em nossos canais de suporte.

## 6. Licença
Este projeto está licenciado sob a [Licença MIT](https://github.com/yourusername/yourproject/blob/main/LICENSE).
