1. Comecei criando a estrutura de arquivos do pipeline deixando a ideia já modelada em todas as etapas do enunciado e instalando todas as dependencias via requirements.txt.
2. Depois de cumprir com a primeira etapa, o segundo passo foi começar a preencher o main.py pois ele é a porta de entrada do pipeline e é necessário validar a interface de entrada antes de qualquer regra de negócio ser aplicada. Criei um arquivo CSV vazio somente para testar a entrada neste passo
3.

TRADE OFF 1: Eu optei por utilizar o FastAPI ao invés do Flask porque o FastAPI tem um modelo robusto, otimizado e já possui documentação automática, isso facilita a sustentação e evolução da API com mais facilidade, sempre que posso escolher utilizo essa biblioteca.

TRADE OFF 2: 