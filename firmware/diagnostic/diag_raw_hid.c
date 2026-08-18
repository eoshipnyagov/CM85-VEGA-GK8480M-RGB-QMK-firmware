/*
 * KD85 VEGA diagnostic bridge, iteration 1.
 *
 * Add this file to the keyboard's QMK target.  It uses QMK's existing VIA
 * Raw HID transport, so the normal keyboard and Vial protocol remain intact.
 * No GPIO, I2C, SPI, external flash, display, or RGB registers are touched.
 */
#include "raw_hid.h"
#include "timer.h"

#include "diag_protocol.h"

static void diag_clear_response(uint8_t *data) {
    for (uint8_t i = 0; i < KD85_DIAG_REPORT_SIZE; ++i) {
        data[i] = 0;
    }
}

static void diag_reply(uint8_t *data, uint8_t status, uint8_t sequence) {
    data[1] = status;
    data[2] = sequence;
    raw_hid_send(data, KD85_DIAG_REPORT_SIZE);
}

/*
 * QMK calls this hook before its own VIA command decoder.  Returning true
 * means that this report has been fully handled and already sent back.
 */
bool via_command_kb(uint8_t *data, uint8_t length) {
    if (length < 2 || data[0] < KD85_DIAG_COMMAND_BASE) {
        return false;
    }

    const uint8_t command  = data[0];
    const uint8_t sequence = data[1];
    diag_clear_response(data);
    data[0] = command;

    switch (command) {
        case KD85_DIAG_PING:
            /* data[3..6] = monotonic milliseconds, useful for transport tests */
            {
                const uint32_t uptime = timer_read32();
                data[3]              = (uint8_t)(uptime >> 24);
                data[4]              = (uint8_t)(uptime >> 16);
                data[5]              = (uint8_t)(uptime >> 8);
                data[6]              = (uint8_t)uptime;
            }
            diag_reply(data, KD85_DIAG_OK, sequence);
            return true;

        case KD85_DIAG_INFO:
            /* ASCII signature and protocol revision, no board-specific claims. */
            data[3] = 1; /* protocol major */
            data[4] = 0; /* protocol minor */
            data[5] = 'K';
            data[6] = 'D';
            data[7] = '8';
            data[8] = '5';
            data[9] = ' ';
            data[10] = 'V';
            data[11] = 'E';
            data[12] = 'G';
            data[13] = 'A';
            diag_reply(data, KD85_DIAG_OK, sequence);
            return true;

        case KD85_DIAG_I2C_SCAN:
        case KD85_DIAG_I2C_READ:
        case KD85_DIAG_SPI_JEDEC:
        case KD85_DIAG_SPI_READ:
            /* Deliberately disabled until the physical pinout is confirmed. */
            diag_reply(data, KD85_DIAG_NOT_IMPLEMENTED, sequence);
            return true;

        default:
            diag_reply(data, KD85_DIAG_UNKNOWN_COMMAND, sequence);
            return true;
    }
}
