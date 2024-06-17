Seja bem-vindo ao InovaAI! Para acessar:

 https://gabrieladourado.pythonanywhere.com/

 Os padroes de Projeto foram:

 SINGLETON,
 FACTORY METHOD e
 OBSERVER.

 Especificando o Singleton: 

 Para a instancia do banco de dados.

 Especificando o FactoryMethod: 
 No caso do UserFactory e ContentRequestFactory, essas classes são responsáveis por encapsular a lógica de criação de novos usuários e solicitações de conteúdo, respectivamente. A necessidade de duas fábricas distintas surge porque cada uma lida com a criação de um tipo diferente de objeto, com propósitos e características diferentes.
 
Embora ambos os métodos de criação (create_user e create_content_request) sigam um padrão semelhante, é importante mantê-los separados para manter a clareza do código e facilitar futuras modificações. Por exemplo, se a lógica de criação de usuários precisar ser alterada, você pode fazer isso sem afetar a lógica de criação de solicitações de conteúdo, e vice-versa.

Portanto, o uso do Factory Method no nosso código ajuda a manter o código mais organizado, seguindo o princípio de responsabilidade única e permitindo uma fácil extensão no futuro, caso seja necessário adicionar novos tipos de objetos ou modificar a lógica de criação existente

 Especificando o Observer: 
 
O objetivo principal da implementação do Observer é notificar os usuários sobre novas solicitações de conteúdo criadas por eles. Isso é feito através da classe UserNotifier, que implementa a interface Observer e se inscreve em instâncias da classe ContentRequest. Quando uma nova solicitação de conteúdo é criada ou editada, o objeto ContentRequest notifica todos os seus observadores registrados, no caso, apenas o UserNotifier. O UserNotifier, ao receber a notificação, utiliza a função flash do Flask para exibir uma mensagem na tela, informando o usuário sobre a nova solicitação.

2. Separação de Preocupações e Flexibilidade:

O uso do padrão Observer promove a separação de preocupações no código, dividindo as responsabilidades entre diferentes classes. A classe ContentRequest se concentra em gerenciar os dados e a lógica da solicitação de conteúdo, enquanto a classe UserNotifier se concentra em notificar os usuários sobre essas solicitações. Essa separação facilita a reutilização e a testabilidade do código.
