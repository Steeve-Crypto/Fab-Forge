import click
import subprocess
from mqtt_layer import FabMQTTClient
from secsgem_layer import SECSGEMEmulator

@click.group()
def cli():
    """Grok CLI for FabForge - Terafab Portfolio Project"""
    pass

@cli.command()
@click.option('--num-wafers', default=10, help='Number of wafers')
@click.option('--steps', default=5, help='Process steps')
def simulate(num_wafers, steps):
    """Run C++ simulation core"""
    print("Running FabForge C++ Simulation...")
    try:
        result = subprocess.run(["./fab_sim"], capture_output=True, text=True, cwd="/home/workdir/artifacts")
        print(result.stdout)
    except Exception as e:
        print(f"Simulation error: {e}")

@cli.command()
@click.option('--topic', required=True)
@click.option('--message')
def mqtt_publish(topic, message):
    """Publish MQTT message"""
    client = FabMQTTClient()
    if client.connect():
        client.publish(topic, message or "test_message")
    else:
        print("Failed to connect to MQTT")

@cli.command()
@click.option('--command', default='START')
@click.option('--wafer-id', default=1, type=int)
def secsgem(command, wafer_id):
    """SECS/GEM protocol emulation"""
    gem = SECSGEMEmulator()
    gem.process_command(command, wafer_id)
    gem.send_stream(2, 17, {"wafer_id": wafer_id})

if __name__ == '__main__':
    cli()
