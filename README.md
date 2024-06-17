Seja bem-vindo ao InovaAI! Para acessar:

 https://gabrieladourado.pythonanywhere.com/

 Os padroes de Projeto foram:

 SINGLETON
 FACTORY METHOD
 OBSERVER

 Especificando o FactoryMethod: 
 No caso do UserFactory e ContentRequestFactory, essas classes são responsáveis por encapsular a lógica de criação de novos usuários e solicitações de conteúdo, respectivamente. A necessidade de duas fábricas distintas surge porque cada uma lida com a criação de um tipo diferente de objeto, com propósitos e características diferentes.
Embora ambos os métodos de criação (create_user e create_content_request) sigam um padrão semelhante, é importante mantê-los separados para manter a clareza do código e facilitar futuras modificações. Por exemplo, se a lógica de criação de usuários precisar ser alterada, você pode fazer isso sem afetar a lógica de criação de solicitações de conteúdo, e vice-versa.
Portanto, o uso do Factory Method no nosso código ajuda a manter o código mais organizado, seguindo o princípio de responsabilidade única e permitindo uma fácil extensão no futuro, caso seja necessário adicionar novos tipos de objetos ou modificar a lógica de criação existente


 
