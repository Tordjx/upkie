// SPDX-License-Identifier: Apache-2.0
// Copyright 2024 Inria
//
// Tests in this file only depend on Eigen, so that we can execute them on x86.

#pragma once

#include <Eigen/Geometry>

namespace upkie::cpp::actuation::pi3hat {

/*! Get raw angular velocity measurement from the gyroscope.
 *
 * \param[in] attitude Attitude object from the pi3hat library.
 * \return Raw angular velocity of the IMU in [rad] / [s].
 */
inline Eigen::Vector3d get_raw_angular_velocity(
    const Eigen::Vector3d& rate_dps, const Eigen::Vector3d& bias_dps) noexcept {
  // https://github.com/mjbots/pi3hat/blob/4a3158c831da125fa9c96d64378515c1fdb2083f/fw/attitude_reference.h#L143
  Eigen::Vector3d current_gyro_dps = rate_dps - bias_dps;
  return current_gyro_dps * M_PI / 180.;
}

/*! Recompute raw linear acceleration from UKF observations.
 *
 * \param[in] orientation_imu_in_ars Rotation from the IMU to the ARS.
 * \param[in] accel_mps2 UKF output linear acceleration, in [m] / [s]².
 * \return Raw linear acceleration in [m] / [s]².
 */
inline Eigen::Vector3d get_raw_linear_acceleration(
    const Eigen::Quaterniond& orientation_imu_in_ars,
    const Eigen::Vector3d& accel_mps2) noexcept {
  // https://github.com/mjbots/pi3hat/blob/4a3158c831da125fa9c96d64378515c1fdb2083f/fw/attitude_reference.h#L186-L187
  Eigen::Vector3d downward_in_world = {0., 0., -1.};
  Eigen::Vector3d downward_in_imu =
      orientation_imu_in_ars.conjugate() * downward_in_world;

  // https://github.com/mjbots/pi3hat/blob/4a3158c831da125fa9c96d64378515c1fdb2083f/fw/attitude_reference.h#L147
  Eigen::Vector3d current_accel_mps2_ = accel_mps2 + 9.81 * downward_in_imu;
  return current_accel_mps2_;
}

}  // namespace upkie::cpp::actuation::pi3hat