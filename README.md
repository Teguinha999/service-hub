Service Hub

Sistema Web para Gerenciamento de Ordens de Serviço e Equipamentos em Assistências Técnicas

1. Sobre o projeto

O Service Hub é uma aplicação web desenvolvida como parte de um Projeto Integrador do curso de Tecnologia da Informação.

O sistema tem como objetivo auxiliar pequenas assistências técnicas na organização de clientes, equipamentos e ordens de serviço, centralizando informações que frequentemente são controladas por processos manuais.

A proposta busca tornar o acompanhamento dos serviços mais organizado, facilitando a consulta de informações e o gerenciamento das atividades da assistência técnica.

2. Funcionalidades

Dashboard: visualização de indicadores de clientes, equipamentos e ordens de serviço.

Gestão de clientes: cadastro, consulta, edição e exclusão protegida de clientes.

Gestão de equipamentos: cadastro e associação de equipamentos aos respectivos clientes.

Ordens de serviço: abertura, consulta, pesquisa, edição e atualização de status.

Histórico de alterações: registro das modificações realizadas nas ordens de serviço, incluindo o motivo informado.

Auditoria de clientes: registro das exclusões permitidas de clientes.

Integridade dos dados: proteção dos relacionamentos entre clientes, equipamentos e ordens de serviço.

3. Tecnologias utilizadas

Python

Flask

SQLite

HTML5

CSS3

JavaScript

Jinja2

4. Estrutura do projeto

ServiceHub/
├── app.py
├── database.py
├── requirements.txt
├── README.md
├── .gitignore
├── templates/
│   ├── index.html
│   ├── clientes.html
│   ├── editar_cliente.html
│   ├── equipamentos.html
│   ├── ordens_servico.html
│   ├── editar_ordem.html
│   └── historico.html
└── static/
    └── css/
        └── style.css

5. Como executar o projeto

Pré-requisitos

Python instalado.

Git instalado.

Clonar o repositório

git clone URL_DO_REPOSITORIO
cd ServiceHub

Criar o ambiente virtual

No Windows:

python -m venv .venv

Ativar o ambiente virtual

.venv\Scripts\Activate.ps1

Instalar as dependências

pip install -r requirements.txt

Executar a aplicação

python app.py

A aplicação poderá ser acessada localmente pelo endereço:

http://127.0.0.1:5000

6. Banco de dados

O projeto utiliza SQLite para armazenar os dados da aplicação.

As tabelas são criadas automaticamente durante a inicialização do sistema. Os relacionamentos entre clientes, equipamentos e ordens de serviço ajudam a preservar a integridade dos registros.

O banco de dados é mantido localmente e não deve conter informações pessoais ou dados reais de clientes no repositório público.

7. Auditoria e integridade

O sistema possui mecanismos de registro de alterações nas ordens de serviço, permitindo consultar os valores anteriores, os novos valores e os motivos informados.

Também existe um registro das exclusões permitidas de clientes.

As restrições de relacionamento do banco de dados impedem exclusões que comprometam registros vinculados.

8. Limitações da versão atual

Esta versão corresponde ao protótipo funcional desenvolvido para fins acadêmicos e de demonstração.

O sistema ainda não possui autenticação de usuários ou controle individual de permissões. A identificação do responsável pelas alterações permanece com um valor padrão enquanto o login não for implementado.

Para utilização em ambiente empresarial, são necessárias avaliações adicionais de segurança, hospedagem, persistência do banco de dados e controle de acesso.

9. Projeto Integrador

Projeto desenvolvido no contexto acadêmico do curso de Tecnologia da Informação.

Nome do projeto: Service Hub

Objetivo: contribuir para a organização e o acompanhamento de serviços em pequenas assistências técnicas.