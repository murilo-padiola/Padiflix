# Padiflix

Padiflix é um gerenciador de filmes desenvolvido em Python e HTML, permitindo organizar e acessar arquivos de vídeo diretamente do navegador.

## Funcionalidades

- Exibe uma lista de filmes armazenados localmente.
- Permite reprodução de vídeos nos formatos MP4, MKV, AVI.
- Interface simples baseada em HTML.
- Armazena informações sobre duração, data de lançamento e avaliações dos filmes, sendo a data de lançamento de forma automática.

## Requisitos

Para executar o Padiflix, você precisará ter instalado:

- Python 3.x
- Um navegador web compatível (Chrome, Firefox, Edge, etc.)
- As seguintes bibliotecas Python:
  ```sh
  pip install flask ffmpeg-python requests
  ```
  Execute o aplicativo abrindo o .bat

## Personalização

- Para adicionar filmes, basta colocá-los na pasta `Filmes/`.
- As informações sobre duração e avaliação estão armazenadas nos arquivos `durations.txt` e `notas.txt`.
- A data de lançamento dos filmes é obtida automaticamente a partir da API TMDb.

## Contribuição

Se quiser melhorar o Padiflix, fique à vontade para enviar pull requests ou relatar problemas na aba de Issues.

## Licença

Este projeto está sob a licença MIT. Sinta-se livre para usá-lo e modificá-lo como desejar.

