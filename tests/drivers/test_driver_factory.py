from __future__ import annotations

import pytest

from workspace_fabric.config import load_config_text
from workspace_fabric.config.models import DriverConfig
from workspace_fabric.drivers import create_driver, create_drivers
from workspace_fabric_driver_mock import MockUsbMatrixDriver, MockVideoMatrixDriver
from workspace_fabric_driver_orei_uhd808 import OreiUhd808VideoDriver
from workspace_fabric_driver_orei_ukm404 import OreiUkm404UsbDriver


def test_driver_factory_creates_mock_and_hardware_drivers() -> None:
    config = load_config_text("""
        version: 1
        fabrics:
          physical_lab: {}
        drivers:
          mock_video:
            type: mock_video_matrix
            fabric: physical_lab
          video_matrix_uhd808:
            type: orei_uhd808
            fabric: physical_lab
            connection:
              transport: telnet
              host: 172.24.2.192
              port: 23
          usb_matrix_ukm404:
            type: orei_ukm404
            fabric: physical_lab
            connection:
              transport: telnet
              host: 172.24.2.193
              port: 23
        """)

    drivers = create_drivers(config.drivers.values())

    assert isinstance(drivers["mock_video"], MockVideoMatrixDriver)
    assert isinstance(drivers["video_matrix_uhd808"], OreiUhd808VideoDriver)
    assert isinstance(drivers["usb_matrix_ukm404"], OreiUkm404UsbDriver)


def test_driver_factory_preserves_mock_usb_driver_support() -> None:
    driver = create_driver(
        DriverConfig(
            id="mock_usb",
            type="mock_usb_matrix",
            fabric="physical_lab",
        )
    )

    assert isinstance(driver, MockUsbMatrixDriver)


def test_driver_factory_rejects_unknown_driver_type() -> None:
    with pytest.raises(ValueError) as exc_info:
        create_driver(
            DriverConfig(
                id="unknown",
                type="not_a_driver",
                fabric="physical_lab",
            )
        )

    assert "Unsupported driver type 'not_a_driver'" in str(exc_info.value)
    assert "orei_uhd808" in str(exc_info.value)
    assert "orei_ukm404" in str(exc_info.value)
