#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 Inria
#
# This file incorporates work covered by the following copyright and
# permission notice:
#
#     setup-system.py from github.com:mjbots/quad
#     Copyright 2018-2020 Josh Pieper
#     SPDX-License-Identifier: Apache-2.0


"""Configure all servos connected to an Upkie wheeled biped."""

import os
import subprocess
import sys
from typing import Union

LEFT_BUS = 1  # JC1
LEFT_HIP = 1
LEFT_KNEE = 2
LEFT_WHEEL = 3

RIGHT_BUS = 3  # JC3
RIGHT_HIP = 4
RIGHT_KNEE = 5
RIGHT_WHEEL = 6

ALL_SERVOS = (
    LEFT_HIP,
    LEFT_KNEE,
    LEFT_WHEEL,
    RIGHT_HIP,
    RIGHT_KNEE,
    RIGHT_WHEEL,
)

UPPER_LEG_SERVOS = (
    LEFT_HIP,
    LEFT_KNEE,
    RIGHT_HIP,
    RIGHT_KNEE,
)

WHEEL_SERVOS = (
    LEFT_WHEEL,
    RIGHT_WHEEL,
)

PI3HAT_CFG = (
    f"{LEFT_BUS}={LEFT_HIP},{LEFT_KNEE},{LEFT_WHEEL}"
    ";"
    f"{RIGHT_BUS}={RIGHT_HIP},{RIGHT_KNEE},{RIGHT_WHEEL}"
)


def run_shell_command(command: str):
    """Run a subprocess."""
    print(f"* {command}")
    subprocess.check_call(command, shell=True)


def configure_servo(servo_id: int, param: str, value: Union[float, str]):
    """Configure a moteus controller.

    Args:
        servo_id: Identifier of the servo to configure.
        param: Parameter to configure.
        value: Value corresponding to the parameter.
    """
    moteus_command = f"conf set {param} {value}"
    shell_command = (
        f'echo "{moteus_command}" | '
        f'sudo moteus_tool --pi3hat-cfg "{PI3HAT_CFG}" -t {servo_id} -c'
    )
    run_shell_command(shell_command)


def write_servo_configuration(servo_id: int):
    """Write configuration to a moteus controller.

    Args:
        servo_id: Identifier of the servo that should write its configuration.
    """
    shell_command = (
        f'echo "conf write" | '
        f'sudo moteus_tool --pi3hat-cfg "{PI3HAT_CFG}" -t {servo_id} -c'
    )
    run_shell_command(shell_command)


def configure_position_limits():
    for hip in (LEFT_HIP, RIGHT_HIP):
        configure_servo(hip, "servopos.position_max", 0.2)
        configure_servo(hip, "servopos.position_min", -0.2)
    for knee in (LEFT_KNEE, RIGHT_KNEE):
        configure_servo(knee, "servopos.position_max", 0.4)
        configure_servo(knee, "servopos.position_min", -0.4)
    for wheel in WHEEL_SERVOS:
        configure_servo(wheel, "servopos.position_max", "NaN")
        configure_servo(wheel, "servopos.position_min", "NaN")


def configure_velocity_limits():
    for hip_or_knee in UPPER_LEG_SERVOS:
        configure_servo(hip_or_knee, "servo.max_velocity", 2.0)
    for wheel in WHEEL_SERVOS:
        configure_servo(wheel, "servo.max_velocity", 8.0)


def configure_default_limits():
    # https://github.com/mjbots/moteus/blob/38d688a933ce1584ee09f2628b5849d5e758ac21/docs/reference.md#servodefault_velocity_limit--servodefault_accel_limit
    for servo in ALL_SERVOS:
        configure_servo(servo, "servo.default_velocity_limit", "NaN")
        configure_servo(servo, "servo.default_accel_limit", "NaN")


def configure_gains():
    for hip_or_knee in UPPER_LEG_SERVOS:
        configure_servo(hip_or_knee, "servo.pid_position.kp", 400.0)
    for wheel in WHEEL_SERVOS:
        # Best value depends wheel radius (WR)
        # Values that have worked well: kd=0.3 for WR=5 cm, kd=0.6 for WR=7 cm
        configure_servo(wheel, "servo.pid_position.kd", 0.3)


if __name__ == "__main__":
    if os.geteuid() != 0:
        args = ["sudo", "-E", sys.executable] + sys.argv + [os.environ]
        os.execlpe("sudo", *args)

    configure_position_limits()
    configure_velocity_limits()
    configure_default_limits()
    configure_gains()
    for servo in ALL_SERVOS:
        write_servo_configuration(servo)
