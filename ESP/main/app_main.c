#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#include <inttypes.h>
#include "esp_system.h"
#include "nvs_flash.h"
#include "esp_event.h"
#include "esp_netif.h"
#include "protocol_examples_common.h"
#include "esp_log.h"
#include "mqtt_client.h"
#include "driver/gpio.h"
#include "freertos/queue.h"
#include "esp_timer.h"

#define GPIO_INPUT_PIN 23               // 입력 핀으로 사용할 GPIO 핀 번호
#define ESP_INTR_FLAG_DEFAULT 0
#define DEBOUNCE_DELAY 200  // 디바운스 지연 시간 (밀리초)


static const char *TAG = "MQTT_GPIO_APP"; // 통합된 TAG
static volatile int button_press_count = 0;  // 버튼 입력 횟수 카운트 변수
volatile unsigned long last_interrupt_time = 0;  // 마지막 인터럽트 발생 시간

static esp_mqtt_client_handle_t client;      // MQTT 클라이언트 핸들
static QueueHandle_t gpio_evt_queue = NULL;  // 버튼 이벤트 큐

// 인터럽트 핸들러
static void IRAM_ATTR gpio_isr_handler(void *arg) {
    // 현재 시간(밀리초 단위)을 읽음
    unsigned long current_time = esp_timer_get_time() / 1000;

    // 마지막 인터럽트와 현재 시간의 차이가 DEBOUNCE_DELAY보다 크면 이벤트 처리
    if (current_time - last_interrupt_time > DEBOUNCE_DELAY) {
        button_press_count++;  // 카운트 증가
        int count = button_press_count;
        xQueueSendFromISR(gpio_evt_queue, &count, NULL);  // 버튼 이벤트를 큐에 전달
        last_interrupt_time = current_time;  // 마지막 인터럽트 발생 시간 갱신
    }
}

// GPIO 초기화 함수
void init_gpio() {
    gpio_config_t io_conf = {
        .intr_type = GPIO_INTR_NEGEDGE,           // 폴링 엣지에서 인터럽트 발생 (버튼 눌림 감지)
        .mode = GPIO_MODE_INPUT,                  // 입력 모드로 설정
        .pin_bit_mask = (1ULL << GPIO_INPUT_PIN), // 제어할 핀 설정
        .pull_down_en = GPIO_PULLDOWN_ENABLE,       // 풀다운 활성화
        .pull_up_en = GPIO_PULLUP_DISABLE          
    };
    gpio_config(&io_conf);

    // GPIO 인터럽트 핸들러 추가
    gpio_install_isr_service(ESP_INTR_FLAG_DEFAULT);
    gpio_isr_handler_add(GPIO_INPUT_PIN, gpio_isr_handler, (void*) GPIO_INPUT_PIN);

    // 성공적으로 GPIO가 설정되었음을 나타내는 로그 출력
    ESP_LOGI(TAG, "GPIO %d successfully configured as input with pull-up enabled and interrupt on negative edge.", GPIO_INPUT_PIN);
}

// 버튼 이벤트 큐를 수신하여 MQTT publish를 수행하는 Task
void mqtt_publish_task(void *arg) {
    int count;
    while (1) {
        // 큐에서 버튼 눌림 이벤트 수신
        if (xQueueReceive(gpio_evt_queue, &count, portMAX_DELAY)) {
            ESP_LOGI(TAG, "Button pressed %d times", count);
            esp_mqtt_client_publish(client, "req/call", "Button press event", 0, 0, 0);
            ESP_LOGI(TAG, "Published button press event to req/call");
        }
    }
}

// MQTT 이벤트 핸들러
static void mqtt_event_handler(void *handler_args, esp_event_base_t base, int32_t event_id, void *event_data) {
    ESP_LOGD(TAG, "Event dispatched from event loop base=%s, event_id=%" PRIi32 "", base, event_id);
    esp_mqtt_event_handle_t event = event_data;
    client = event->client;

    switch ((esp_mqtt_event_id_t)event_id) {
        case MQTT_EVENT_CONNECTED:
            ESP_LOGI(TAG, "MQTT_EVENT_CONNECTED");
            esp_mqtt_client_publish(client, "req/call", "Hello", 0, 0, 0);
            break;
        case MQTT_EVENT_DATA:
            ESP_LOGI(TAG, "MQTT_EVENT_DATA");
            printf("TOPIC=%.*s\r\n", event->topic_len, event->topic);
            printf("DATA=%.*s\r\n", event->data_len, event->data);
            break;
        default:
            ESP_LOGI(TAG, "Other event id:%d", event->event_id);
            break;
    }
}

// MQTT 초기화 함수
static void mqtt_app_start(void) {
    esp_mqtt_client_config_t mqtt_cfg = {
        .broker.address.uri = CONFIG_BROKER_URL,
    };

    client = esp_mqtt_client_init(&mqtt_cfg);
    esp_mqtt_client_register_event(client, ESP_EVENT_ANY_ID, mqtt_event_handler, NULL);
    esp_mqtt_client_start(client);
}

void app_main(void) {
    ESP_LOGI(TAG, "Initializing GPIO...");
    init_gpio();       // GPIO 초기화

    ESP_LOGI(TAG, "[APP] Startup..");
    ESP_LOGI(TAG, "[APP] Free memory: %" PRIu32 " bytes", esp_get_free_heap_size());
    ESP_LOGI(TAG, "[APP] IDF version: %s", esp_get_idf_version());

    ESP_ERROR_CHECK(nvs_flash_erase());
    ESP_ERROR_CHECK(nvs_flash_init());
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    ESP_ERROR_CHECK(example_connect());

    ESP_LOGI(TAG, "Initializing MQTT...");
    mqtt_app_start();  // MQTT 초기화

    // 버튼 이벤트 큐 생성 및 MQTT publish Task 생성
    gpio_evt_queue = xQueueCreate(10, sizeof(int));
    xTaskCreate(mqtt_publish_task, "mqtt_publish_task", 4096, NULL, 10, NULL);

    while (1) {
        vTaskDelay(pdMS_TO_TICKS(1000));  // 1초 대기
    }
}
