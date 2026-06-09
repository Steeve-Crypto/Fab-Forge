#pragma once
#include <string>
#include <map>

enum class EquipmentState {
    IDLE,
    PROCESSING,
    MAINTENANCE,
    FAULT
};

class EquipmentStateMachine {
public:
    EquipmentStateMachine(const std::string& name);
    void transition(EquipmentState newState);
    void transitionTo(EquipmentState newState);  // compatibility for bindings
    EquipmentState getCurrentState() const;
    std::string getStatus() const;
    bool processWafer(int waferId);

private:
    std::string name_;
    EquipmentState currentState_;
    std::map<EquipmentState, std::string> stateDescriptions_;
};
