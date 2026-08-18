/*
 * KD85 VEGA diagnostic protocol, iteration 1.
 *
 * Reports are 32 bytes, matching the report size observed in the original
 * firmware.  The protocol is deliberately read-only in this iteration.
 */
#pragma once

#include <stdint.h>

#define KD85_DIAG_REPORT_SIZE 32
#define KD85_DIAG_COMMAND_BASE 0xE0

enum kd85_diag_command {
    KD85_DIAG_PING = 0xE0,
    KD85_DIAG_INFO = 0xE1,
    KD85_DIAG_I2C_SCAN = 0xE2, /* reserved; not enabled in iteration 1 */
    KD85_DIAG_I2C_READ = 0xE3, /* reserved; not enabled in iteration 1 */
    KD85_DIAG_SPI_JEDEC = 0xE4, /* reserved; not enabled in iteration 1 */
    KD85_DIAG_SPI_READ = 0xE5, /* reserved; not enabled in iteration 1 */
};

enum kd85_diag_status {
    KD85_DIAG_OK = 0x00,
    KD85_DIAG_BAD_LENGTH = 0x01,
    KD85_DIAG_UNKNOWN_COMMAND = 0x02,
    KD85_DIAG_NOT_IMPLEMENTED = 0x03,
};

/* Request:  [command, sequence, payload ...]
 * Response: [command, status, sequence, payload ...]
 */
