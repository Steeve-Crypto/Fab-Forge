#include "Wafer.h"
#include <iostream>

Wafer::Wafer(int id) : id_(id), yield_(1.0) {}

void Wafer::processStep(const std::string& step, double duration) {
    processHistory_.push_back(step);
    // Simulate yield degradation
    yield_ *= (1.0 - 0.001 * duration);
    std::cout << "Wafer " << id_ << " processed " << step << " for " << duration << "s. Yield: " << yield_ << std::endl;
}

double Wafer::getYield() const { return yield_; }
int Wafer::getId() const { return id_; }
