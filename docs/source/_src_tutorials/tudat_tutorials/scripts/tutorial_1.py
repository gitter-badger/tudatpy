###############################################################################
# IMPORT STATEMENTS ###########################################################
###############################################################################
import numpy as np
from tudatpy import constants
from tudatpy import elements
from tudatpy import io
from tudatpy import ephemerides
from tudatpy import interpolators
from tudatpy import numerical_integrators
from tudatpy import spice_interface
from tudatpy import basic_astrodynamics
# from tudatpy import orbital_element_conversions # LEGACY MODULE
from tudatpy import propagators
from tudatpy import aerodynamics
from tudatpy import simulation_setup


def main():
    # Load spice kernels.
    spice_interface.load_standard_kernels()

    # Set simulation start epoch.
    simulation_start_epoch = 0.0

    # Set numerical integration fixed step size.
    fixed_step_size = 1.0

    # Set simulation end epoch.
    simulation_end_epoch = constants.JULIAN_DAY

    ###########################################################################
    # CREATE ENVIRONMENT ######################################################
    ###########################################################################

    # Create body objects.
    bodies_to_create = ["Earth"]

    body_settings = simulation_setup.get_default_body_settings(bodies_to_create)

    body_settings["Earth"].ephemeris_settings = simulation_setup.ConstantEphemerisSettings(
        np.zeros(6))

    body_settings["Earth"].rotation_model_settings.reset_original_frame("ECLIPJ2000")

    # Create Earth Object.
    bodies = simulation_setup.create_bodies(body_settings)

    ###########################################################################
    # CREATE VEHICLE ##########################################################
    ###########################################################################

    # Create vehicle objects.
    bodies["Delfi-C3"] = simulation_setup.Body()

    ###########################################################################
    # FINALIZE BODIES #########################################################
    ###########################################################################

    simulation_setup.set_global_frame_body_ephemerides(bodies, "SSB",
                                                       "ECLIPJ2000")

    ###########################################################################
    # CREATE ACCELERATIONS ####################################################
    ###########################################################################

    # Define bodies that are propagated.
    bodies_to_propagate = ["Delfi-C3"]

    # Define central bodies.
    central_bodies = ["Earth"]

    # Define accelerations acting on Delfi-C3.
    accelerations_of_delfi_c3 = dict(
        Earth=[simulation_setup.Acceleration.point_mass_gravity()]
    )

    # Create global accelerations dictionary.
    accelerations = {"Delfi-C3": accelerations_of_delfi_c3}

    # Create acceleration models.
    acceleration_models = simulation_setup.create_acceleration_models_dict(
        bodies, accelerations, bodies_to_propagate, central_bodies)

    ###########################################################################
    # CREATE PROPAGATION SETTINGS #############################################
    ###########################################################################

    # Set initial conditions for the Asterix satellite that will be
    # propagated in this simulation. The initial conditions are given in
    # Keplerian elements and later on converted to Cartesian elements.

    # Set Keplerian elements for Delfi-C3
    earth_gravitational_parameter = bodies[
        "Earth"].gravity_field_model.get_gravitational_parameter()

    # LEGACY DESIGN.
    # KEI = orbital_element_conversions.KeplerianElementIndices
    # asterix_initial_state_in_keplerian_elements = np.zeros(6)
    # kep_state = asterix_initial_state_in_keplerian_elements
    # kep_state[int(KEI.semi_major_axis_index)] = 7500.0E3
    # kep_state[int(KEI.eccentricity_index)] = 0.1
    # kep_state[int(KEI.inclination_index)] = np.deg2rad(85.3)
    # kep_state[int(KEI.argument_of_periapsis_index)] = np.deg2rad(235.7)
    # kep_state[int(KEI.longitude_of_ascending_node_index)] = np.deg2rad(23.4)
    # kep_state[int(KEI.true_anomaly_index)] = np.deg2rad(139.87)
    # system_initial_state = corbital_element_conversions.onvert_keplerian_to_cartesian_elements(
    #     kep_state, earth_gravitational_parameter)

    # REVISED CONTEMPORARY DESIGN.
    system_initial_state = elements.keplerian2cartesian(
        mu=earth_gravitational_parameter,
        a=7500.0E3,
        ecc=0.1,
        inc=np.deg2rad(85.3),
        raan=np.deg2rad(23.4),
        argp=np.deg2rad(235.7),
        nu=np.deg2rad(139.87))

    # Create propagation settings.
    propagator_settings = propagators.TranslationalStatePropagatorSettings(
        central_bodies,
        acceleration_models,
        bodies_to_propagate,
        system_initial_state,
        simulation_end_epoch
    )
    # Create numerical integrator settings.
    integrator_settings = numerical_integrators.IntegratorSettings(
        numerical_integrators.AvailableIntegrators.rungeKutta4,
        simulation_start_epoch,
        fixed_step_size
    )

    ###########################################################################
    # PROPAGATE ORBIT #########################################################
    ###########################################################################

    # Create simulation object and propagate dynamics.
    dynamics_simulator = propagators.SingleArcDynamicsSimulator(
        bodies, integrator_settings, propagator_settings, True)
    result = dynamics_simulator.get_equations_of_motion_numerical_solution()

    ###########################################################################
    # PRINT INITIAL AND FINAL STATES ##########################################
    ###########################################################################

    print(
        f"""
Single Earth-Orbiting Satellite Example.
The initial position vector of Delfi-C3 is [km]: \n{
        result[simulation_start_epoch][:3] / 1E3}
The initial velocity vector of Delfi-C3 is [km]: \n{
        result[simulation_start_epoch][3:] / 1E3}
After {simulation_end_epoch} seconds the position vector of Delfi-C3 is [km]: \n{
        result[simulation_end_epoch][:3] / 1E3}
And the velocity vector of Delfi-C3 is [km]: \n{
        result[simulation_start_epoch][3:] / 1E3}
        """
    )

    ###########################################################################
    # SAVE RESULTS ############################################################
    ###########################################################################

    io.save2txt(
        solution=result,
        filename="singleSatellitePropagationHistory.dat",
        directory="./tutorial_1",
    )

    # Final statement (not required, though good practice in a __main__).
    return 0


if __name__ == "__main__":
    main()
