// #include <WiFi.h>
// #include <PubSubClient.h>
// #include "DHT.h"
// #include <time.h>  // Adicionado para NTP

// // ======== CONFIGURAÇÕES WI-FI ========
// const char* ssid = "o nome do seu wifi";
// const char* password = "sua senha do wifi";

// // ======== CONFIGURAÇÕES MQTT ========
// const char* mqtt_server = "seu ip local";
// const int mqtt_port = 1883;
// const char* mqtt_topic = "api-fatec/estacao/dados/";

// // ======== CONFIGURAÇÕES DHT ========
// #define DHTPIN 32
// #define DHTTYPE DHT11
// DHT dht(DHTPIN, DHTTYPE);

// // ======== CONFIGURAÇÕES NTP ========
// const char* ntpServer = "pool.ntp.org";  // Servidor NTP global
// const long gmtOffset_sec = -3 * 3600;    // GMT-3 (Brasil)
// const int daylightOffset_sec = 0;         // Sem horário de verão

// // ======== OBJETOS ========
// WiFiClient espClient;
// PubSubClient client(espClient);

// // ======== INTERVALO DE ENVIO ========
// unsigned long lastMsg = 0;
// const long interval = 30000;  // 30 segundos

// // ======== VARIÁVEIS GLOBAIS ========
// unsigned int leituras_falhas = 0;
// const unsigned int MAX_TENTATIVAS_SENSOR = 3;
// unsigned long ultimaLeituraValida = 0;

// // Função para obter o UID único da placa ESP32 (JÁ FUNCIONA BEM!)
// String getDeviceUID() {
//   uint64_t chipid = ESP.getEfuseMac();
//   char uid[20];
//   snprintf(uid, sizeof(uid), "%04X%08X", (uint16_t)(chipid >> 32), (uint32_t)chipid);
//   return String(uid);
// }

// // Configura o NTP (Network Time Protocol)
// void configNTP() {
//   configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
//   Serial.println("Sincronizando horário com NTP...");
  
//   struct tm timeinfo;
//   if (!getLocalTime(&timeinfo)) {
//     Serial.println("Falha ao obter horário NTP");
//     return;
//   }
//   Serial.println(&timeinfo, "Horário configurado: %A, %d %B %Y %H:%M:%S");
// }

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
//     delay(200); // Intervalo crítico para o DHT11
    
//     // Lê os valores brutos
//     float temp_raw = dht.readTemperature();
//     float umid_raw = dht.readHumidity();
    
//     Serial.print("Leitura bruta - Tentativa ");
//     Serial.print(i);
//     Serial.print(": Temp=");
//     Serial.print(temp_raw);
//     Serial.print("C, Umidade=");
//     Serial.print(umid_raw);
//     Serial.println("%");

//     // Filtro de validação rigoroso
//     if (isnan(temp_raw) || isnan(umid_raw)) {
//       Serial.println("Valores inválidos (NaN)");
//       continue;
//     }

//     // Faixas realistas para interior em clima temperado
//     if (temp_raw >= -5 && temp_raw <= 50 && 
//         umid_raw >= 10 && umid_raw <= 95) {
//       temperatura = temp_raw;
//       umidade = umid_raw;
//       ultimaLeituraValida = millis();
      
//       // Filtro adicional para temperaturas negativas
//       if (temperatura < 0) {
//         Serial.println("Ajustando temperatura negativa para 0");
//         temperatura = 0.0; // Valor mínimo realista para interior
//       }
      
//       return true;
//     }
//     else {
//       Serial.println("Valores fora da faixa realista");
//     }
    
//     if (i < MAX_TENTATIVAS_SENSOR) delay(1000);
//   }
  
//   leituras_falhas++;
//   return false;
// }


// void setup() {
//   Serial.begin(115200);
//   Serial.println("\nInicializando estação meteorológica...");
  
//   dht.begin();
//   delay(2000);
  
//   setup_wifi();
//   configNTP();  // Sincroniza o horário
  
//   client.setServer(mqtt_server, mqtt_port);
//   client.setBufferSize(256);
//   client.setKeepAlive(60);
// }

// void loop() {
//   if (!client.connected()) {
//     reconnect();
//   }
//   client.loop();

  unsigned long now = millis();
  if (now - lastMsg > interval) {
    lastMsg = now;

//     float temperatura = NAN;
//     float umidade = NAN;
//     bool leituraOk = false;

//     Serial.println("\nIniciando leitura do sensor...");
//     leituraOk = lerDHT11(temperatura, umidade);
    
//     if (leituraOk) {
//       struct tm timeinfo;
//       getLocalTime(&timeinfo);  // Obtém horário atual
//       time_t unixTime = mktime(&timeinfo);

//       char payload[256];
//       snprintf(payload, sizeof(payload),
//         "{\"uid\":\"%s\",\"temp\":%.2f,\"umid\":%.2f,\"unixtime\":%ld}",
//         getDeviceUID().c_str(), temperatura, umidade, unixTime
//       );

//       Serial.print("Enviando: ");
//       Serial.println(payload);
      
//       if (!client.publish(mqtt_topic, payload)) {
//         Serial.println("Erro ao publicar no MQTT!");
//       }
//     } else {
//       Serial.println("Falha na leitura do sensor");
//     }
//   }
//   delay(50);
// }