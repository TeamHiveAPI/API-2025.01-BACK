// #include <WiFi.h>
// #include <PubSubClient.h>
// #include "DHT.h"

// // ======== CONFIGURAÇÕES WI-FI ========
// const char* ssid = "nome da sua rede";
// const char* password = "senha da sua rede";

// // ======== CONFIGURAÇÕES MQTT ========
// const char* mqtt_server = "ip local da sua maquina";
// const int mqtt_port = 1883;
// const char* mqtt_topic = "api-fatec/estacao/dados/";

// // ======== CONFIGURAÇÕES DHT ========
// #define DHTPIN 14
// #define DHTTYPE DHT11
// DHT dht(DHTPIN, DHTTYPE);

// // ======== OBJETOS ========
// WiFiClient espClient;
// PubSubClient client(espClient);

// // ======== INTERVALO DE ENVIO ========
// unsigned long lastMsg = 0;
// const long interval = 600000; // 10 minutos

// // ======== VARIÁVEIS GLOBAIS ========
// unsigned int leituras_falhas = 0;
// const unsigned int MAX_TENTATIVAS_SENSOR = 3;
// unsigned long ultimaLeituraValida = 0;

// void setup_wifi() {
//   delay(100);
//   Serial.print("Conectando ao Wi-Fi: ");
//   Serial.println(ssid);

//   WiFi.begin(ssid, password);
//   while (WiFi.status() != WL_CONNECTED) {
//     delay(1000);
//     Serial.print(".");
//   }

//   Serial.println("\nWi-Fi conectado!");
//   Serial.print("IP: ");
//   Serial.println(WiFi.localIP());
// }

// void reconnect() {
//   while (!client.connected()) {
//     Serial.print("Conectando ao MQTT...");
//     if (client.connect("ESP32Client")) {
//       Serial.println("Conectado!");
//     } else {
//       Serial.print("Falha, rc=");
//       Serial.print(client.state());
//       Serial.println(" Tentando novamente em 5 segundos");
//       delay(5000);
//     }
//   }
// }

// bool lerDHT11(float &temperatura, float &umidade) {
//   for (int i = 1; i <= MAX_TENTATIVAS_SENSOR; i++) {
//     // Limpa qualquer estado anterior do sensor
//     delay(200);
    
//     temperatura = dht.readTemperature();
//     umidade = dht.readHumidity();
    
//     Serial.print("Tentativa ");
//     Serial.print(i);
//     Serial.print(": Temp=");
//     Serial.print(temperatura);
//     Serial.print("C, Umidade=");
//     Serial.print(umidade);
//     Serial.println("%");

//     // Verificação robusta dos valores
//     if (!isnan(temperatura) && !isnan(umidade)) {
//       if (temperatura >= -20 && temperatura <= 60 && // Faixa ampliada
//           umidade >= 5 && umidade <= 95) {           // Faixa ampliada
//         ultimaLeituraValida = millis();
//         return true;
//       }
//       Serial.println("Valores fora da faixa esperada");
//     }
    
//     if (i < MAX_TENTATIVAS_SENSOR) {
//       delay(1500); // Intervalo menor entre tentativas
//     }
//   }
  
//   leituras_falhas++;
//   Serial.print("Falha na leitura após ");
//   Serial.print(MAX_TENTATIVAS_SENSOR);
//   Serial.println(" tentativas");
//   return false;
// }

// void setup() {
//   Serial.begin(115200);
//   Serial.println("\nInicializando estação meteorológica...");
  
//   // Inicializa sensor com timeout
//   dht.begin();
//   delay(2000); // Tempo crítico para inicialização do DHT11
  
//   Serial.println("Sensor DHT11 inicializado");
//   setup_wifi();
  
//   client.setServer(mqtt_server, mqtt_port);
//   client.setBufferSize(256);
//   client.setKeepAlive(60); // Keepalive de 60 segundos
// }

// void loop() {
//   if (!client.connected()) {
//     reconnect();
//   }
//   client.loop();

//   unsigned long now = millis();
//   if (now - lastMsg > interval) {
//     lastMsg = now;

//     float temperatura = NAN;
//     float umidade = NAN;
//     bool leituraOk = false;
    
//     Serial.println("\nIniciando leitura do sensor...");
//     leituraOk = lerDHT11(temperatura, umidade);

//     // Prepara payload com todos os cenários
//     char payload[256];
//     if (leituraOk) {
//       snprintf(payload, sizeof(payload),
//         "{\"uid\":\"esp32-dht11-001\",\"temp\":%.2f,\"umid\":%.2f,\"status\":\"OK\",\"falhas\":%u}",
//         temperatura, umidade, leituras_falhas
//       );
//     } else {
//       snprintf(payload, sizeof(payload),
//         "{\"uid\":\"esp32-dht11-001\",\"temp\":null,\"umid\":null,\"status\":\"ERRO\",\"falhas\":%u}",
//         leituras_falhas
//       );
//     }

//     // Publica independentemente do status
//     Serial.print("Enviando: ");
//     Serial.println(payload);
    
//     if (!client.publish(mqtt_topic, payload)) {
//       Serial.println("Erro ao publicar no MQTT!");
//     }

//     // Informações de diagnóstico
//     Serial.print("Última leitura válida há ");
//     Serial.print((millis() - ultimaLeituraValida) / 1000);
//     Serial.println(" segundos");
//     Serial.print("Total de falhas: ");
//     Serial.println(leituras_falhas);
//   }
  
//   delay(50); // Pequeno delay para estabilidade
// }