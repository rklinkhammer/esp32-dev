#include "esp_log.h"

/* Build-environment check only: no motor, permit, or board GPIO operations. */
void app_main(void)
{
    ESP_LOGI("esp32-dev", "Native ESP-IDF build environment ready");
}
