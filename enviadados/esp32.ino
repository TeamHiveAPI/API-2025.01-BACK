// #include <WiFi.h>
// #include <PubSubClient.h>
// #include "DHT.h"
// #include <time.h>

// // ======== CONFIGURAÇÃO DO BUZZER ========
// #define PIN_BUZZER 4  // Trocar se necessário

// // ======== CONFIGURAÇÃO DO LED ========
// #define PIN_LED_PULSO 33

// // ======== CONFIGURAÇÕES WI-FI ========
// const char* ssid = "g84 Ivan";
// const char* password = "Ivan1403";

// // ======== CONFIGURAÇÕES MQTT ========
// const char* mqtt_server = "192.168.95.119";
// const int mqtt_port = 1883;
// const char* mqtt_topic = "api-fatec/estacao/dados/";

// // ======== CONFIGURAÇÕES TEMT6000 =====
// const int TEMT6000_PIN = 32;
// const int THRESHOLD_LUZ = 300;  // Ajuste conforme ambiente

// // ======== CONFIGURAÇÕES DHT ========
// #define DHTPIN 14
// #define DHTTYPE DHT22
// DHT dht(DHTPIN, DHTTYPE);

// // ======== CONFIGURAÇÕES NTP ========
// const char* ntpServer = "pool.ntp.org";
// const long gmtOffset_sec = -10800;
// const int daylightOffset_sec = 0;

// // ======== CONFIGURAÇÕES PULSOS ========
// #define PIN_PULSO 13
// volatile unsigned int total_pulsos = 0;
// volatile unsigned long ultimaInterrupcao = 0;
// volatile bool primeiroPulso = true;

// // ======== OBJETOS ========
// WiFiClient espClient;
// PubSubClient client(espClient);

// // ======== VARIÁVEIS GLOBAIS ========
// unsigned long lastMsg = 0;
// const long interval = 30000;
// unsigned int leituras_falhas = 0;
// const unsigned int MAX_TENTATIVAS_SENSOR = 3;

// // ======== FUNÇÕES ========
// String getDeviceUID() {
//   uint64_t chipid = ESP.getEfuseMac();
//   char uid[20];
//   snprintf(uid, sizeof(uid), "%04X%08X", (uint16_t)(chipid >> 32), (uint32_t)chipid);
//   return String(uid);
// }

// int lerLuminosidadeRaw() {
//   int valor = analogRead(TEMT6000_PIN);
//   Serial.print("Luminosidade bruta (lux): ");
//   Serial.println(valor);
//   return valor;
// }

// String interpretarPeriodo(int valor) {
//   return (valor > THRESHOLD_LUZ) ? "dia" : "noite";
// }

// void acionarSirene(bool alarme) {
//   if (!alarme) return;

//   const int intervalo = 5000;
//   const int duracaoSom = 300;
//   const int tempoTotal = 30000;
//   unsigned long tempoInicio = millis();

//   while (millis() - tempoInicio < tempoTotal) {
//     digitalWrite(PIN_BUZZER, HIGH);
//     delay(duracaoSom);
//     digitalWrite(PIN_BUZZER, LOW);
//     delay(intervalo - duracaoSom);
//   }
// }

// void IRAM_ATTR contarPulso() {
//   unsigned long agora = millis();
//   if (primeiroPulso || (agora - ultimaInterrupcao > 180000)) {
//     total_pulsos++;
//     ultimaInterrupcao = agora;
//     primeiroPulso = false;

//     digitalWrite(PIN_LED_PULSO, HIGH);
//     ets_printf("Pulso contado! Total: %u\n", total_pulsos);
//   }
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
//   vTaskDelete(NULL);
// }

// void TaskMQTT(void* parameter) {
//   client.setServer(mqtt_server, mqtt_port);
//   client.setBufferSize(512);
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

//     Serial.printf("Leitura bruta - Tentativa %d: Temp=%.2f°C, Umid=%.2f%%\n", i, temp_raw, umid_raw);

//     if (isnan(temp_raw) || isnan(umid_raw)) {
//       Serial.println("Valores inválidos (NaN)");
//       continue;
//     }

//     if (temp_raw >= -5 && temp_raw <= 50 && umid_raw >= 10 && umid_raw <= 95) {
//       temperatura = temp_raw < 0 ? 0.0 : temp_raw;
//       umidade = umid_raw;
//       return true;
//     }

//     Serial.println("Valores fora da faixa realista");
//     if (i < MAX_TENTATIVAS_SENSOR) delay(1000);
//   }

//   leituras_falhas++;
//   return false;
// }

// // ======== SETUP ========
// void setup() {
//   Serial.begin(115200);
//   Serial.println("\nInicializando estação meteorológica...");
//   dht.begin();

//   pinMode(PIN_LED_PULSO, OUTPUT);
//   digitalWrite(PIN_LED_PULSO, LOW);

//   pinMode(PIN_PULSO, INPUT);
//   attachInterrupt(digitalPinToInterrupt(PIN_PULSO), contarPulso, RISING);

//   pinMode(PIN_BUZZER, OUTPUT);
//   digitalWrite(PIN_BUZZER, LOW);

//   xTaskCreate(TaskWiFi, "WiFiTask", 4096, NULL, 1, NULL);
//   xTaskCreate(TaskMQTT, "MQTTTask", 4096, NULL, 1, NULL);
// }

// // ======== LOOP PRINCIPAL ========
// void loop() {
//   if (client.connected()) {
//     client.loop();
//   }

//   unsigned long now = millis();
//   if (now - lastMsg > interval) {
//     lastMsg = now;

//     float temperatura = NAN;
//     float umidade = NAN;

//     Serial.println("\nIniciando leitura dos sensores...");

//     int lux = lerLuminosidadeRaw();
//     String periodo = interpretarPeriodo(lux);

//     if (lerDHT11(temperatura, umidade)) {
//       struct tm timeinfo;
//       if (getLocalTime(&timeinfo)) {
//         time_t unixTime = mktime(&timeinfo);

//         char payload[256];
//         snprintf(payload, sizeof(payload),
//           "{\"uid\":\"%s\",\"temp\":%.2f,\"umid\":%.2f,\"lux\":%d,\"pulsos\":%u,\"unixtime\":%ld}",
//           getDeviceUID().c_str(), temperatura, umidade, lux, total_pulsos, unixTime
//         );

//         Serial.print("Enviando: ");
//         Serial.println(payload);

//         if (!client.publish(mqtt_topic, payload)) {
//           Serial.println("Erro ao publicar no MQTT!");
//         }
//       } else {
//         Serial.println("Horário ainda não disponível. Pulo do envio.");
//       }
//     } else {
//       Serial.println("Falha na leitura do sensor DHT.");
//     }
//   }

//   delay(50);
//   digitalWrite(PIN_LED_PULSO, LOW);
// }