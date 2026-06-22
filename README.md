# Pipeline Teste via CLI

O projeto foi desenvolvido para atender um teste prático com foco em Python, automações, integração com APIs, tratamento de dados inconsistentes e idempotência.

## Visão Geral

O pipeline executa o seguinte fluxo:

1. Lê um arquivo CSV disponível na pasta `input/`, criando uma landing zone.
2. Normaliza os campos esperados.
3. Valida os registros conforme as regras do enunciado.
4. Separa registros válidos e inválidos no `output/`.
5. Remove duplicidades por `external_id` mantendo a última ocorrência válida.
6. Enriquece registros válidos com endereço pela API do ViaCEP.
7. Cadastra ou atualiza os registros em uma API mock local.
8. Gera arquivos de saída na pasta `output/`.
9. Gera relatório JSON e log de execução.

## Estrutura do Projeto

```text
pipeline_cli_teste/
  input/
    clientes.csv
  output/
    valid.csv
    invalid.csv
    report.json
    execution.log
  src/
    normalizer.py
    validator.py
    writer.py
    viacep_client.py
    internal_api_client.py
    report.py
    logger.py
  tests/
    test_normalizer.py
    test_validator.py
  api_mock.py
  main.py
  requirements.txt
  pytest.ini
  README.md
```

## Requisitos

- Python 3.13 ou superior
- Ambiente virtual Python
- Acesso à internet para consulta ao ViaCEP

## Instalação

Crie e ative o ambiente virtual:

```bash
python -m venv .venv
```

```bash
.\.venv\Scripts\Activate.ps1
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Dependências utilizadas:

```text
fastapi
uvicorn
requests
pytest
```

## Como Executar

Primeiro suba a API localmente em um terminal separado:

```bash
uvicorn api_mock:app --reload
```

A API ficará disponível em:

```text
http://127.0.0.1:8000
```

Em outro terminal execute o pipeline:

```bash
python main.py --input input/clientes.csv
```

## Como Rodar os Testes

Execute:

```bash
pytest
```

Os testes cobrem:

- normalização de campos;
- validação de registros inválidos;
- deduplicação por `external_id`.

## Arquivo de Entrada

O CSV pode conter as seguintes colunas:

```text
external_id
name
email
document
phone
zip_code
```

Colunas extras são ignoradas no processamento.

## Regras de Normalização

Para cada registro:

- espaços extras são removidos;
- email é convertido para lowercase;
- `document`, `phone` e `zip_code` mantêm apenas números;
- colunas extras são ignoradas.

## Regras de Validação

As validações aplicadas são:

- `external_id`: obrigatório;
- `name`: obrigatório, com mínimo de 2 caracteres;
- `email`: opcional, mas se informado precisa ter formato válido;
- `document`: opcional, mas se informado precisa ter 11 ou 14 dígitos;
- `phone`: opcional, mas se informado precisa conter apenas números após normalização;
- `zip_code`: opcional, mas se informado precisa conter exatamente 8 dígitos.

Registros inválidos não interrompem a execução, eles são enviados para `output/invalid.csv` com o motivo da invalidação.

## Deduplicação e Idempotência

O controle de duplicidade é feito por `external_id`.

Quando o mesmo `external_id` aparece mais de uma vez no CSV o pipeline mantém a última ocorrência válida.

A idempotência também é garantida na API mock local:

- se o `external_id` ainda não existir, o registro é criado e a API retorna `201`;
- se o `external_id` já existir, o registro é atualizado e a API retorna `200`.

Rodar o pipeline duas vezes com o mesmo arquivo não cria duplicidade.

## Enriquecimento ViaCEP

Para registros válidos com `zip_code`, o pipeline consulta:

```text
https://viacep.com.br/ws/{zip_code}/json/
```

Quando a consulta retorna endereço, são adicionados os campos:

```text
street
neighborhood
city
state
```

Se a API falhar ou o CEP não for encontrado, o pipeline registra a falha, mantém o processamento e grava os campos de endereço vazios.

## API Mock Interna

A API mockada foi implementada com FastAPI e SQLite.

Endpoint:

```http
POST /clients
```

Persistência:

```text
pipeline_cli_teste.db
```

Regra de escrita:

- `external_id` é a chave primária;
- registro novo retorna `201`;
- registro existente retorna `200`;
- registros existentes são atualizados.

## Arquivos de Saída

O pipeline gera a pasta `output/` com:

```text
valid.csv
invalid.csv
report.json
execution.log
```

### valid.csv

Contém os registros válidos, normalizados, deduplicados e enriquecidos via ViaCEP.

### invalid.csv

Contém os campos originais esperados do CSV e o motivo da invalidação.

### report.json

Contém:

```json
{
  "total_processados": 
  "total_validos": 
  "total_invalidos": 
  "total_criados": 
  "total_atualizados": 
  "total_falhas_api": 
  "tempo_execucao": 
}
```

### execution.log

Contém logs com timestamp, nível e mensagem.

Exemplo:

```text
2026-06-22 17:19:14 | INFO | Total de registros processados: 7
```
### Warnings

O pipeline registra warnings para situações que não devem interromper a execução mas precisam ficar rastreáveis no log.

Atualmente são registrados warnings para:

- registros inválidos encontrados durante a validação;
- `external_id` duplicado no arquivo de entrada;
- falha ou ausência de retorno na consulta ao ViaCEP.

Exemplos:

```text
2026-06-22 17:19:14 | WARNING | Registro inválido: external_id=003 motivo=O campo 'EMAIL' é inválido.
2026-06-22 17:19:14 | WARNING | External ID duplicado encontrado: 001
2026-06-22 17:19:14 | WARNING | Falha ao consultar a API do ViaCEP para o zip_code=99999999
```

### Tratamento de Erros

O pipeline foi estruturado para não interromper a execução por erro em registros individuais.

Principais tratamentos:

- registros inválidos são separados em `invalid.csv`;
- falhas no ViaCEP não interrompem o processamento;
- falhas na API interna são contabilizadas;
- arquivos de saída são gerados mesmo que alguma lista esteja vazia;
- logs registram início, fim, totais e falhas relevantes.

## Premissas Adotadas

- O CSV pode vir em `utf-8-sig` ou `cp1252`.
- Colunas extras não fazem parte do processamento final.
- CPF e CNPJ são validados apenas pelo tamanho numérico, sem validação oficial de dígitos.
- Para duplicidades no mesmo CSV, a última ocorrência válida por `external_id` prevalece.
- A API mock precisa estar rodando para que o cadastro interno retorne criação ou atualização.
- O arquivo `output/` é resultado de execução e pode ser recriado pelo pipeline.

## Decisões Técnicas

- Usei `csv.DictReader` para não depender da ordem das colunas.
- Separei responsabilidades em módulos dentro de `src/` para manter o `main.py` como orquestrador do fluxo.
- Usei FastAPI pela simplicidade, documentação automática e boa estrutura para APIs.
- Usei SQLite por ser nativo, simples de executar localmente e suficiente para demonstrar idempotência.
- Mantive timeout nas chamadas externas para evitar que o pipeline fique preso aguardando resposta.
- Usei `pytest` para cobrir regras centrais de normalização, validação e deduplicação.

## Limitações

- Não há autenticação na API mock pois não era exigido no escopo e seria algo que eu implementaria.
- Não há retry/backoff nas chamadas ao ViaCEP, então este ponto fica ok.
- A validação de CPF/CNPJ considera apenas quantidade de dígitos no código que fiz, porém em uma implementação real poderíamos evoluir para uma API da Receita Federal para validação inteligente desse campo.

## Uso de IA

Usei IA como apoio durante o desenvolvimento para revisar decisões técnicas e discutir trade-offs. As decisões de estrutura, validação, fluxo de execução, criação do código, ajustes finais e testes foram executadas manualmente por mim durante a implementação, limitando o uso de IA para revisão.

## Anotações de Desenvolvimento

Durante o desenvolvimento segui uma evolução incremental do pipeline.

- Primeiro criei a estrutura inicial de arquivos para refletir as etapas do enunciado.

- Depois comecei pelo `main.py` pois ele é a porta de entrada do pipeline e antes de aplicar regra de negócio validei a interface exigida pelo teste:

```bash
python main.py --input arquivo.csv
```

- Em seguida criei um CSV de teste com dados válidos, inválidos, duplicados e colunas extras. Essa etapa ajudou a validar a ingestão real do arquivo e também revelou uma questão de encoding como arquivos criados ou editados no Windows podem vir em `cp1252` e arquivos vindo de sistemas (APIs) podem vir em `utf-8` implementei um fallback entre `utf-8-sig` e `cp1252` para tornar a leitura mais robusta.

- Na etapa de normalização criei funções específicas para limpar textos, normalizar email e manter apenas números em campos como documento, telefone e CEP. Depois integrei essa lógica ao `main.py` e passei a exibir uma prévia do dataset antes e depois da normalização.

- Com os dados normalizados implementei o `validator.py`. Nele concentrei as regras de validação do enunciado e também adicionei uma validação simples de email com regex. A função principal retorna se a linha é válida e quando não é, retorna o motivo da invalidação.

- Depois criei o `writer.py` para centralizar a escrita dos arquivos de saída, uma decisão importante foi gerar os arquivos com cabeçalho mesmo quando não houver linhas porque isso mantém o output do pipeline previsível em todos os cenários.

- Também tratei duplicidade por `external_id`, a regra adotada foi manter a última ocorrência válida do arquivo.

- Na sequência implementei o `viacep_client.py` responsável por consultar a API pública do ViaCEP e mapear os campos retornados para `street`, `neighborhood`, `city` e `state`.

- Depois implementei a API mockada em `api_mock.py` usando FastAPI e SQLite. Escolhi SQLite por ser simples, nativo e suficiente para demonstrar persistência local. Com a API rodando validei o comportamento idempotente com seguinte teste: na primeira execução os registros foram criados e na segunda execução os mesmos registros foram atualizados.

- Em seguida implementei o `report.py` responsável por montar e escrever o `report.json` com os totais exigidos no enunciado do teste.

- Por fim implementei o `logger.py` usando a biblioteca nativa `logging`, o logger registra início e fim da execução, totais processados, falhas de API e arquivos gerados.

- Depois que o fluxo principal estava atendido adicionei testes unitários simples para normalização, validação e deduplicação. A intenção foi garantir uma checagem rápida das regras mais críticas do enunciado.

## Trade-offs

- Optei por FastAPI em vez de Flask porque o FastAPI oferece uma estrutura moderna, documentação automática e boa integração com modelos de entrada usando Pydantic.

- Também optei por separar responsabilidades em módulos, entendo que isso aumenta um pouco a quantidade de arquivos mas melhora a leitura, facilita manutenção e reduz o risco de o `main.py` concentrar regra demais e acoplar o pipeline. A ideia é deixar sempre ele preparado para escalar por isso eu prefiro esse estilo de programação.
