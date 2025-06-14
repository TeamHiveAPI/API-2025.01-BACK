// #include <WiFi.h>
// #include <PubSubClient.h>
// #include "DHT.h"
// #include <time.h>

// // ======== CONFIGURAÇÕES WI-FI ========
// const char* ssid = "g84 Ivan";
// const char* password = "Ivan1403";

// // ======== CONFIGURAÇÕES MQTT ========
// const char* mqtt_server = "192.168.85.119";
// const int mqtt_port = 1883;
// const char* mqtt_topic = "api-fatec/estacao/dados/";

// // ======== CONFIGURAÇÕES DHT ========
// #define DHTPIN 32
// #define DHTTYPE DHT11
// DHT dht(DHTPIN, DHTTYPE);

// // ======== CONFIGURAÇÕES NTP ========
// const char* ntpServer = "192.168.85.119";
// const long gmtOffset_sec = -10800;
// const int daylightOffset_sec = 0;

// // ======== OBJETOS ========
// WiFiClient espClient;
// PubSubClient client(espClient);

// // ======== VARIÁVEIS GLOBAIS ========
// unsigned long lastMsg = 0;
// const long interval = 30000;
// unsigned int leituras_falhas = 0;
// const unsigned int MAX_TENTATIVAS_SENSOR = 3;
// unsigned long ultimaLeituraValida = 0;

// // ========== FUNÇÕES AUXILIARES ==========

// String getDeviceUID() {
//   uint64_t chipid = ESP.getEfuseMac();
//   char uid[20];
//   snprintf(uid, sizeof(uid), "%04X%08X", (uint16_t)(chipid >> 32), (uint32_t)chipid);
//   return String(uid);
// }

// void configNTP() {
//   configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
//   Serial.println("Sincronizando horário com NTP...");

//   struct tm timeinfo;
//   int tentativas = 0;
//   while (!getLocalTime(&timeinfo) && tentativas < 10) {
//     Serial.print(".");
//     delay(500);
//     tentativas++;
//   }

//   if (tentativas >= 10) {
//     Serial.println("\nFalha ao obter horário NTP");
//   } else {
//     Serial.println("\nHorário NTP sincronizado com sucesso!");
//     Serial.println(&timeinfo, "Horário atual: %A, %d %B %Y %H:%M:%S");
//   }
// }

// void TaskWiFi(void* parameter) {
//   delay(100);
//   Serial.print("Conectando ao Wi-Fi: ");
//   Serial.println(ssid);

//   WiFi.begin(ssid, password);
//   while (WiFi.status() != WL_CONNECTED) {
//     Serial.print(".");
//     vTaskDelay(1000 / portTICK_PERIOD_MS);
//   }

//   Serial.println("\nWi-Fi conectado!");
//   Serial.print("IP: ");
//   Serial.println(WiFi.localIP());

//   configNTP();
//   vTaskDelete(NULL);  // Task executa uma vez e termina
// }

// void TaskMQTT(void* parameter) {
//   client.setServer(mqtt_server, mqtt_port);
//   client.setBufferSize(256);
//   client.setKeepAlive(60);

//   while (true) {
//     if (WiFi.status() == WL_CONNECTED && !client.connected()) {
//       Serial.print("Conectando ao MQTT...");
//       if (client.connect("ESP32Client")) {
//         Serial.println("Conectado!");
//       } else {
//         Serial.print("Falha, rc=");
//         Serial.print(client.state());
//         Serial.println(" Tentando novamente em 5 segundos...");
//       }
//     }
//     vTaskDelay(5000 / portTICK_PERIOD_MS);
//   }
// }

// bool lerDHT11(float &temperatura, float &umidade) {
//   for (int i = 1; i <= MAX_TENTATIVAS_SENSOR; i++) {
//     delay(200);
//     float temp_raw = dht.readTemperature();
//     float umid_raw = dht.readHumidity();

//     Serial.print("Leitura bruta - Tentativa ");
//     Serial.print(i);
//     Serial.print(": Temp=");
//     Serial.print(temp_raw);
//     Serial.print("C, Umidade=");
//     Serial.print(umid_raw);
//     Serial.println("%");

//     if (isnan(temp_raw) || isnan(umid_raw)) {
//       Serial.println("Valores inválidos (NaN)");
//       continue;
//     }

//     if (temp_raw >= -5 && temp_raw <= 50 && umid_raw >= 10 && umid_raw <= 95) {
//       temperatura = temp_raw < 0 ? 0.0 : temp_raw;
//       umidade = umid_raw;
//       ultimaLeituraValida = millis();
//       return true;
//     } else {
//       Serial.println("Valores fora da faixa realista");
//     }

//     if (i < MAX_TENTATIVAS_SENSOR) delay(1000);
//   }

//   leituras_falhas++;
//   return false;
// }

// // ========== SETUP E LOOP PRINCIPAL ==========

// void setup() {
//   Serial.begin(115200);
//   Serial.println("\nInicializando estação meteorológica...");
//   dht.begin();

//   // Criando as tasks
//   xTaskCreate(TaskWiFi, "WiFiTask", 4096, NULL, 1, NULL);
//   xTaskCreate(TaskMQTT, "MQTTTask", 4096, NULL, 1, NULL);
// }

// void loop() {
//   if (client.connected()) {
//     client.loop();
//   }

//   unsigned long now = millis();
//   if (now - lastMsg > interval) {
//     lastMsg = now;

//     float temperatura = NAN;
//     float umidade = NAN;

//     Serial.println("\nIniciando leitura do sensor...");
//     if (lerDHT11(temperatura, umidade)) {
//       struct tm timeinfo;
//       if (getLocalTime(&timeinfo)) {
//         time_t unixTime = mktime(&timeinfo);

//         char payload[256];
//         snprintf(payload, sizeof(payload),
//           "{\"uid\":\"%s\",\"temp\":%.2f,\"umid\":%.2f,\"unixtime\":%ld}",
//           getDeviceUID().c_str(), temperatura, umidade, unixTime
//         );

//         Serial.print("Enviando: ");
//         Serial.println(payload);

//         if (!client.publish(mqtt_topic, payload)) {
//           Serial.println("Erro ao publicar no MQTT!");
//         }
//       } else {
//         Serial.println("Horário NTP ainda não disponível. Pulo do envio.");
//       }
//     } else {
//       Serial.println("Falha na leitura do sensor.");
//     }
//   }

//   delay(50);
// }