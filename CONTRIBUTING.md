# Contributing Guide — DARA

Obrigado pelo interesse em contribuir com o DARA!

O DARA é uma plataforma desenvolvida para auxiliar empresas do ramo alimentício na compreensão e aplicação de práticas ESG (Environmental, Social and Governance), incentivando uma gestão mais consciente e sustentável.

Este documento apresenta orientações para desenvolvedores que desejam colaborar com o projeto, sugerir melhorias ou corrigir problemas.

## 1. Como começar

Antes de contribuir, é necessário configurar o ambiente de desenvolvimento local.

### Pré-requisitos

- Python 3.12 ou superior.
- Git.
- Conhecimentos básicos de Python, Django, HTML e CSS.

### Configuração do ambiente

1. Clone o repositório:

   ```bash
   git clone URL_DO_REPOSITORIO
   cd dara
   ```

2. Crie e ative um ambiente virtual:

   **Windows:**
   ```bash
   py -m venv venv
   venv\Scripts\activate
   ```

   **Linux / macOS:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

4. Execute as migrações:

   ```bash
   py manage.py migrate
   ```

5. Crie um usuário administrador, caso necessário:

   ```bash
   py manage.py createsuperuser
   ```

6. Inicie o servidor:

   ```bash
   py manage.py runserver
   ```

O projeto estará disponível em:

http://127.0.0.1:8000/

> Observação: substitua `URL_DO_REPOSITORIO` e `dara` pelos dados reais do repositório e da pasta do projeto.

## 2. Organização e arquitetura

O DARA utiliza o padrão MVT (Model-View-Template), adotado pelo Django.

Ao contribuir, procure respeitar a separação de responsabilidades:

- **Models:** responsáveis pela estrutura e representação dos dados.
- **Views:** responsáveis pela lógica de processamento e comunicação entre as requisições e os templates.
- **Templates:** responsáveis pela estrutura e apresentação das páginas HTML.
- **Static:** arquivos estáticos, como CSS, JavaScript, imagens e outros recursos visuais.

Evite concentrar responsabilidades diferentes em um único arquivo.

## 3. Diretrizes de desenvolvimento

Para manter a consistência do projeto, siga estas recomendações:

- Mantenha o código organizado e legível.
- Utilize nomes descritivos para variáveis, funções, classes e arquivos.
- Evite duplicação desnecessária de código.
- Preserve as funcionalidades já implementadas.
- Respeite a estrutura existente do projeto.
- Comente trechos de código quando sua lógica não for evidente.
- Verifique se as alterações não provocam erros em outras funcionalidades.

## 4. Identidade visual

A identidade visual do DARA deve ser preservada em todas as contribuições relacionadas à interface.

Ao desenvolver ou modificar páginas, considere as seguintes orientações:

- Respeite o manual de identidade visual da marca.
- Mantenha a consistência entre cores, tipografia, elementos gráficos e espaçamentos.
- Preserve a unidade visual entre as diferentes páginas.
- Evite utilizar fotografias realistas ou elementos visuais que não estejam alinhados à proposta da marca.
- Priorize uma interface intuitiva, acessível e organizada.

Novos componentes visuais devem seguir os padrões já estabelecidos no projeto.

## 5. Fluxo de navegação

O fluxo principal de utilização do DARA deve ser preservado:

1. Landing page.
2. Escolha de perfil.
3. Área do dono.
4. Questionário ESG.
5. Home.

O sistema possui diferentes perfis de usuário, incluindo donos e funcionários.

Alterações na autenticação, no cadastro ou no redirecionamento entre páginas devem considerar as responsabilidades e permissões de cada perfil.

## 6. Funcionalidades e regras de negócio

Ao modificar funcionalidades existentes, considere as regras estabelecidas:

- O questionário ESG deve ser preenchido pelo dono durante seu primeiro acesso, no processo de criação do perfil.
- O questionário não deve exigir um novo preenchimento a cada acesso.
- As informações cadastradas pela empresa devem ser preservadas durante a navegação.
- As funcionalidades devem respeitar as permissões de cada perfil.
- Os formulários devem apresentar informações claras sobre erros e preenchimento.

Qualquer alteração nessas regras deve ser cuidadosamente avaliada para evitar inconsistências no funcionamento do sistema.

## 7. Como propor melhorias

Antes de implementar uma nova funcionalidade ou alteração significativa:

1. Verifique se a funcionalidade já existe.
2. Analise como a proposta se relaciona com a arquitetura atual.
3. Identifique quais arquivos poderão ser afetados.
4. Avalie possíveis impactos nas funcionalidades existentes.
5. Apresente a proposta e sua justificativa.

Mudanças estruturais ou visuais significativas devem ser discutidas antes da implementação.

## 8. Como enviar contribuições

Recomendamos utilizar branches separadas para organizar o desenvolvimento.

1. Crie uma branch para sua alteração:

   ```bash
   git checkout -b nome-da-sua-branch
   ```

2. Realize as modificações necessárias.
3. Verifique o funcionamento das funcionalidades alteradas.
4. Faça commits com mensagens claras e objetivas:

   ```bash
   git add .
   git commit -m "Descrição da alteração"
   ```

5. Envie sua branch:

   ```bash
   git push origin nome-da-sua-branch
   ```

6. Abra um Pull Request, descrevendo as alterações realizadas e seus objetivos.

## 9. Relatando problemas

Ao identificar um erro, forneça o máximo possível de informações para facilitar sua análise:

- Descrição do problema.
- Etapas para reproduzi-lo.
- Comportamento esperado.
- Comportamento observado.
- Mensagens de erro ou capturas de tela, quando disponíveis.

## 10. Considerações finais

Toda contribuição deve buscar fortalecer os objetivos do DARA, preservando sua identidade, organização e propósito.

Agradecemos a todos que dedicam seu tempo para contribuir com o desenvolvimento do projeto!
