// SPDX-License-Identifier: Apache-2.0
// Copyright 2022 Stéphane Caron

#pragma once

#include <palimpsest/Dictionary.h>

#include "upkie/cpp/observation/Observer.h"

namespace upkie::cpp::observation::tests {

//! Exception-throwing observer
class ThrowingObserver : public observation::Observer {
 public:
  void read(const palimpsest::Dictionary& observation) override {
    throw std::runtime_error("could not get schwifty");
  }
};

}  // namespace upkie::cpp::observation::tests
