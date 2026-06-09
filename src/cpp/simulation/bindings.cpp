#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "FabSimulator.h"
#include "Wafer.h"
#include "PLCEngine.h"
#include "EquipmentStateMachine.h"

namespace py = pybind11;

PYBIND11_MODULE(fabforge_cpp, m) {
    m.doc() = "FabForge C++ core with PyBind11 bindings";

    py::class_<Wafer>(m, "Wafer")
        .def(py::init<int>())
        .def("get_id", &Wafer::getId)
        .def("process", &Wafer::process);

    py::class_<FabSimulator>(m, "FabSimulator")
        .def(py::init<>())
        .def("run_simulation", &FabSimulator::runSimulation)
        .def("add_equipment", &FabSimulator::addEquipment);

    // Add more bindings as needed for PLC, StateMachine etc.
    py::class_<PLCEngine>(m, "PLCEngine")
        .def(py::init<>())
        .def("execute_rung", &PLCEngine::executeRung);

    py::class_<EquipmentStateMachine>(m, "EquipmentStateMachine")
        .def(py::init<const std::string&>())
        .def("transition_to", &EquipmentStateMachine::transitionTo)
        .def("get_current_state", &EquipmentStateMachine::getCurrentState);
}
