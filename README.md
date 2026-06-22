1. Comecei criando a estrutura de arquivos do pipeline deixando a ideia já modelada em todas as etapas do enunciado e instalando todas as dependencias via requirements.txt.
2. Depois de cumprir com a primeira etapa, o segundo passo foi começar a preencher o main.py pois ele é a porta de entrada do pipeline e é necessário validar a interface de entrada antes de qualquer regra de negócio ser aplicada. Criei um arquivo CSV vazio somente para testar a entrada neste passo
3. Nesta etapa inseri um arquivo CSV com dados mockados para já testar a ingestão do arquivo com coluna e linhas, gerando uma exibição da prévia dos dados ingeridos no terminal. Tive um pequeno erro em relação ao encoding onde foi informado que arquivos editados manualmente (eu criei o CSV manualmente) tem um encoding diferente de arquivos gerados via sistema, então eu resolvi criar um fallback para que ambos os encodings sejam testados aumentando a robustez na etapa de ingestão sendo preparada para ambos os tipos de arquivo.
4. Nesta etapa estruturei o script para normalização dos dados conforme o enunciado do teste, onde eu criei 3 funções para realizar essa tarefa, a primeira foi only_digits onde ele remove do campo tudo o que não for número, a segunda foi o normalize_text que remove os espaços no começo e fim, a terceira foi o normalize_email que remove espaços e transforma todos os caracteres em letras minusculas, por fim criei o normalize_row que recebe a linha crua do CSV de entrada e devolve a linha limpa usando as funções criadas. Em seguida passei a usar o normalize_row dentro do main.py para integrar o resultado desse processamento no pipeline. Também atualizei o console para ele exibir o dataset antes e depois do tratamento de normalização.





TRADE OFF 1: Eu optei por utilizar o FastAPI ao invés do Flask porque o FastAPI tem um modelo robusto, otimizado e já possui documentação automática, isso facilita a sustentação e evolução da API com mais facilidade, sempre que posso escolher utilizo essa biblioteca.

TRADE OFF 2: 