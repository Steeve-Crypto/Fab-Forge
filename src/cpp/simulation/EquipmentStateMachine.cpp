#include "EquipmentStateMachine.h"
#include <iostream>

EquipmentStateMachine::EquipmentStateMachine(const std::string& name) 
    : name_(name), currentState_(EquipmentState::IDLE) {
    stateDescriptions_[EquipmentState::IDLE] = "Idle - Ready for next wafer";
    stateDescriptions_[EquipmentState::PROCESSING] = "Processing wafer";
    stateDescriptions_[EquipmentState::MAINTENANCE] = "Under maintenance";
    stateDescriptions_[EquipmentState::FAULT] = "Fault detected";
}

void EquipmentStateMachine::transition(EquipmentState newState) {
    std::cout << name_ << ": Transitioning from " 
              << getStatus() << " to " << stateDescriptions_[newState] << std::endl;
    currentState_ = newState;
}

EquipmentState EquipmentStateMachine::getCurrentState() const {
    return currentState_;
}

std::string EquipmentStateMachine::getStatus() const {
    return stateDescriptions_.at(currentState_);
}

bool EquipmentStateMachine::processWafer(int waferId) {
    if (currentState_ == EquipmentState::IDLE) {
        transition(EquipmentState::PROCESSING);
        std::cout << name_ << ": Processing wafer " << waferId << std::endl;
        // Simulate processing time
        transition(EquipmentState::IDLE);
        return true;
    }
    return false;
}
