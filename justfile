# Tasks for this repository. Run `just` to list them.

default:
    @just --list

# Lint, format-check and validate every action
lint:
    uvx pre-commit run --all-files

# Validate every */action.yaml (pins, metadata, README)
check:
    ./scripts/check_actions.py

# Report image pins that are behind the latest stable release
pins-check:
    ./scripts/update_image_pins.py --check

# Rewrite image pins to the latest stable release (tag + digest)
update-pins:
    ./scripts/update_image_pins.py
