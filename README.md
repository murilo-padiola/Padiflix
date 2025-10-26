# Padiflix

Padiflix é um gerenciador de filmes desenvolvido em Python e HTML, permitindo organizar e acessar arquivos de vídeo diretamente do navegador.

## Funcionalidades

- Exibe uma lista de filmes armazenados localmente.
- Permite reprodução de vídeos nos formatos MP4, MKV, AVI, MOV, FLV, HTML.
- Interface simples baseada em HTML.
- Armazena informações sobre duração, data de lançamento e avaliações dos filmes, sendo a data de lançamento de forma automática.

## Requisitos

Para executar o Padiflix, você precisará ter instalado:

- Python 3.x (eu uso 3.13)
- Um navegador web compatível (Chrome, Firefox, Edge, etc.)
- As seguintes bibliotecas Python:
  ```sh
  pip install flask ffmpeg-python requests colorthief
  ```
  Execute o aplicativo abrindo o `PadiFlix.bat`

Coloque suas chaves da tmdb (https://developer.themoviedb.org/docs/getting-started) e da omdb (https://www.omdbapi.com/apikey.aspx) no keys.txt nos devidos lugares

## Personalização

- Para adicionar filmes, basta colocá-los na pasta `Filmes/` em formato '.mp4', '.mkv', '.avi', '.mov', '.flv' ou até '.html' (usar HTML irá gerar problemas quanto à duração do filme, mas tem a vantagem de não gastar espaço quase algum).
- Colocar as capas em .jpg no `/static/covers`, usando o mesmo título que os nomes dos arquivos dos filmes
- As informações sobre duração, data de lançamento e avaliação estão armazenadas nos arquivos `durations.txt`, `data.txt` e `notas.txt`.
- A data de lançamento e nota dos filmes é obtida automaticamente a partir das APIs TMDb e OMDB.

## Contribuição

Se quiser melhorar o Padiflix, fique à vontade para enviar pull requests ou relatar problemas na aba de Issues.

## Licença

Este projeto está sob a licença MIT. Sinta-se livre para usá-lo e modificá-lo como desejar.

