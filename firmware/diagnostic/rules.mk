# Include in the KD85 QMK target's rules.mk.
# RAW_ENABLE is already required by VIA; keeping it explicit documents the
# transport on which the diagnostic protocol rides.
RAW_ENABLE = yes

# Add the source file from this directory to the keyboard target.
SRC += $(ROOT_DIR)/../vega-reverse/firmware/diagnostic/diag_raw_hid.c
