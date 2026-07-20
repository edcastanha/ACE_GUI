Contexto

A Kunos Simulazioni introduziu o suporte a mods de carros (arquivos .spkg) e pinturas personalizadas (External Liveries) a partir da atualização 0.8 do Assetto Corsa Evo (ACE). O processo manual atual é fragmentado e exige que os jogadores naveguem por diretórios ocultos do Windows ou mapeiem prefixos emulados do Proton no Linux para gerenciar arquivos .json e estruturas de pastas.
Problema

A alta fricção do processo manual gera erros frequentes (como digitação incorreta de IDs alfanuméricos em arquivos de configuração de pinturas), dificulta o gerenciamento de conteúdo e cria barreiras complexas para jogadores no Linux/Steam Deck que tentam localizar os caminhos emulados do jogo. Não há um utilitário nativo prático que faça a instalação por cliques e permita a remoção limpa do conteúdo instalado.
Objetivo

Desenvolver uma aplicação desktop multiplataforma (Windows/Linux) utilizando Python, com uma interface gráfica (GUI) moderna e intuitiva, focada em automatizar a detecção de caminhos de instalação, realizar o processamento inteligente de arquivos (instalação via apontamento de .zip e pacotes .spkg) e permitir a desinstalação segura e completa de conteúdos adicionais com um clique.
Não Objetivos (Escopo Fora)

    Edição de texturas ou criação de arquivos de skin (designing).

    Gerenciamento ou configuração de servidores dedicados multiplayer.

    Suporte a outros simuladores da franquia (AC1 ou ACC).

Solução Proposta (Detalhada)

    Mapeamento e Busca Dinâmica de Caminhos:

        Na primeira execução, o app realiza uma busca varrendo os caminhos padrões do sistema. No Windows: %USERPROFILE%\Saved Games\ACE\. No Linux: busca automatizada no diretório padrão do Steam Apps pelo prefixo do Proton (.../compatdata/1548780/pfx/drive_c/users/.../Saved Games/ACE).

        Interface inicial apresenta os caminhos encontrados para validação do usuário ou seletor manual caso o jogo esteja em uma biblioteca customizada.

    Painel de Controle Visual Híbrido:

        Listagem em tempo real da garagem do usuário baseado nos dados lidos de profile_data/.../saved_cars.

        Painel central mostrando os carros modificados instalados e as pinturas ativas.

    Processamento e Vínculo Inteligente:

        Carros (.spkg): O usuário aponta o arquivo baixado, o app descompacta e move para a pasta /Mods.

        Pinturas (.zip): O app descompacta os arquivos em /External Liveries, exibe um modal listando os carros da garagem do usuário para que ele selecione o veículo correto e injeta automaticamente o GUID/ID do carro no campo carguide dentro do JSON de configuração da livery.

    Interface de Remoção Unificada:

        Ao lado de cada mod ou pintura ativa no painel do app, haverá um botão de exclusão. O app remove os arquivos físicos e as pastas de forma limpa, revertendo alterações de configuração sem afetar outros dados do jogo.

Alternativas Consideradas

    Electron (TypeScript): Descartado para evitar o overhead de performance e o tamanho de pacote (80MB+) que o Chromium exige, especialmente operando paralelamente a jogos via Proton no Linux.

    C# (.NET Core + AvaloniaUI): Considerado, mas o Python oferece maior flexibilidade de scripts e manuseio de strings de caminhos variados para a comunidade de modding Linux de forma mais direta.

Impacto Técnico (Alto Nível)

    Stack: Python 3.x.

    Interface: Flet (Flutter engine para Python) ou PySide6 com folhas de estilo modernas para garantir o visual moderno e nativo.

    Bibliotecas de Sistema: os, pathlib, shutil e zipfile para o controle preciso de I/O de arquivos.

Métricas de Sucesso (KPIs)

    Tempo de Processamento: Redução no tempo de instalação de liveries de minutos para menos de 30 segundos.

    Confiabilidade: Zero erros de sintaxe ou aspas mal posicionadas no preenchimento de arquivos de configuração.

    Adoção Cross-Platform: Funcionamento idêntico da interface e ferramentas em ambientes Windows e Linux.

Riscos e Mitigação

    Risco: Atualizações da Kunos alterarem o nome ou a estrutura das propriedades dos arquivos JSON de save.

    Mitigação: Centralizar a camada de leitura/escrita de arquivos de configuração em uma classe isolada no Python, facilitando correções rápidas via patch.

    Pontos de Clarificação

    Dúvida 1 (Automação do Site Overtake): O site Overtake (antigo RaceDepartment) exige login do usuário para realizar o download de arquivos e possui proteções contra bots (como Cloudflare). A integração automática no painel exibirá apenas a listagem (via raspagem de dados/API interna se houver) ou o app deverá abrir uma janela de login/WebView embutida para autenticar a conta gratuita do usuário e realizar o download direto pelo painel?

    Dúvida 2 (Padrão de Interface com Flet/PySide6): Para garantir o visual moderno solicitado, utilizaremos o Flet (que usa o motor do Flutter e facilita designs consistentes em Windows e Linux) ou o PySide6 (Qt completo para Python)? Recomendação de PO: O Flet acelerará a entrega da interface moderna com menos código.

    Decisão Pendente (Mapeamento Linux/Proton): No Linux, o jogo roda em sandboxes isoladas do Steam/Proton (geralmente sob o AppID 1548780, caso seja esse o ID do ACE). O app deve varrer os diretórios padrão do Steam (~/.steam/steam/steamapps/compatdata/...) automaticamente ou incluímos um botão explícito de "Buscar biblioteca Steam" caso o usuário use caminhos customizados (como Flatpak ou múltiplos HDs)?

    Risco Não Resolvido (Extração de Arquivos .SPKG): O formato .spkg é o pacote nativo da Kunos. O vídeo mostra que ele é apenas extraído/copiado para a pasta /Mods. Precisamos confirmar se ele é um formato zip compactado padrão renomeado (o que permite extração nativa via biblioteca zipfile do Python) ou se exige alguma ferramenta de descompactação proprietária.

    📑 BACKLOG ESTRUTURADO (FASE 5: PLAN)🎯 ÉPICO 1: Core da Aplicação & Configuração de AmbienteObjetivo: Estabelecer a base do software em Python + Flet, garantindo a inicialização do app, interface base e a localização correta do diretório do jogo no Windows.US01: Mapeamento Automático do Diretório do JogoComo jogador de Assetto Corsa Evo,quero que o aplicativo identifique a pasta de saves do jogo automaticamente na primeira execução,para que eu não precise procurar caminhos complexos no Windows manualmente.Critérios de Aceitação:O aplicativo deve buscar por padrão a variável de ambiente %USERPROFILE%\Saved Games\ACE\.Se as pastas /Mods e /External Liveries não existirem no diretório raiz do ACE, o aplicativo deve criá-las silenciosamente.Caso o caminho padrão não seja encontrado, o aplicativo deve exibir uma tela inicial amigável solicitando que o usuário selecione a pasta manualmente via seletor de arquivos.Definition of Ready (DoR):[x] Escopo claro: Focado apenas em Windows para a V1 (caminho Linux postergado para Fase 2).[x] Dependências: Acesso às bibliotecas nativas os e pathlib do Python.[x] Objetivo validado: Garantir que o app saiba onde ler e escrever arquivos.🎯 ÉPICO 2: Integração com API & Painel de DescobertaObjetivo: Construir a interface visual moderna em Flet que consome os dados da API externa para listar e baixar conteúdos categorizados.US02: Painel de Navegação de Mods e Liveries (Flet GUI)Como jogador de Assetto Corsa Evo,quero visualizar um catálogo visual de carros e pinturas categorizados dentro do app,para descobrir novos conteúdos sem sair da aplicação.Critérios de Aceitação:A interface deve ser construída em Flet seguindo padrões visuais modernos (cards com imagens, tags de categoria e descrições limpas).O app deve fazer uma requisição GET para a API externa para listar os dados estruturados por Categoria -> Modelo do Carro -> Conteúdo (Pinturas disponíveis).Cada item listado deve apresentar um botão claro de "Instalar".Definition of Ready (DoR):[x] Escopo claro: Painel puramente visual baseado no JSON retornado pela API.[x] Dependências: Estrutura do payload da API externa definida; biblioteca requests ou httpx no Python.🎯 ÉPICO 3: Instalação e Vínculo Inteligente de ConteúdoObjetivo: Desenvolver o motor de download, extração e injeção de configurações nos arquivos do jogo de forma 100% automatizada.US03: Instalação Automatizada de Mods de CarroComo jogador de Assetto Corsa Evo,quero clicar em instalar um carro do catálogo,para que o app baixe o .zip, extraia e envie o arquivo .spkg para a pasta correta de mods.Critérios de Aceitação:Ao clicar em "Instalar" em um card de carro, o app faz o download do pacote .zip da API em background (mostrando uma barra de progresso).O backend em Python deve descompactar o arquivo temporariamente.O arquivo .spkg contido no zip deve ser copiado diretamente para a pasta %USERPROFILE%\Saved Games\ACE\Mods\.Definition of Ready (DoR):[x] Escopo claro: Fluxo de Download -> Unzip -> Copy do arquivo .spkg.US04: Instalação e Vínculo Assistido de Pinturas (Liveries)Como jogador de Assetto Corsa Evo,quero associar uma pintura baixada a um carro específico da minha garagem com um clique,para que o vínculo do ID no arquivo de configuração funcione sem eu precisar editar textos.Critérios de Aceitação:O app deve ler a pasta de carros criados pelo usuário em profile_data/.../saved_cars e listar esses carros na interface.Ao baixar uma pintura, um modal deve abrir perguntando: "Em qual carro da sua garagem deseja aplicar esta pintura?".Após a seleção do usuário, o Python deve ler o JSON da pintura baixada, injetar o GUID/ID do carro selecionado na propriedade carguide (mantendo as aspas) e salvar o arquivo em /External Liveries.Definition of Ready (DoR):[x] Escopo claro: Manipulação do JSON da livery com base na escolha do carro do usuário.🎯 ÉPICO 4: Gerenciamento e Remoção de ConteúdoObjetivo: Garantir o ciclo de vida completo do mod, permitindo que o usuário limpe seu armazenamento facilmente.US05: Desinstalação Segura de Mods e PinturasComo jogador de Assetto Corsa Evo,quero visualizar o que já tenho instalado e ter a opção de remover qualquer item,para manter as pastas do meu jogo limpas e livres de arquivos residuais.Critérios de Aceitação:O painel deve exibir uma aba ou indicador visual de "Instalado" nos itens presentes localmente nas pastas /Mods e /External Liveries.Ao lado dos itens instalados, deve haver um botão "Remover".Ao clicar em remover, o Python deve deletar fisicamente o arquivo .spkg correspondente ou a pasta da livery de forma limpa, atualizando o status na interface imediatamente.Definition of Ready (DoR):[x] Escopo claro: Exclusão de arquivos físicos mapeados localmente via interface.📊 Matriz de Priorização (Esforço x Impacto)IDStoryImpactoEsforçoRiscoUrgênciaPrioridadeUS01Mapeamento Automático do DiretórioAltoBaixoBaixoCrítica1º (Bloqueante)US03Instalação de Mods de CarroAltoMédioBaixoAlta2ºUS04Instalação e Vínculo de PinturasAltíssimoAltoMédioAlta3ºUS02Painel de Navegação (Flet GUI)MédioMédioBaixoMédia4ºUS05Desinstalação SeguraMédioBaixoBaixoMédia5º