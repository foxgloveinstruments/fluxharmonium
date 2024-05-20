# fluxharmonium
hardware and software for the fluxharmonium

## Hardware

Hardware design files for the primary electronics are located in the `kicad` of each primary function; [conductor](hardware/conductor/kicad), [ensemble](hardware/ensemble/kicad/), and [output](hardware/output/kicad).

## Software

The embedded microcontroller is currently a [Pimoroni Tiny2040 8MB](https://shop.pimoroni.com/products/tiny-2040) running CircuitPython. Firmware for the controller is located in the [src folder](src/)


Tested with Adafruit CircuitPython 8.0.5 on 2023-03-31; Pimoroni Tiny 2040 (8MB) with rp2040