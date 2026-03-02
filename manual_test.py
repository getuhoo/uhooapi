import asyncio
import aiohttp
from uhooapi.client import Client


async def main():
    async with aiohttp.ClientSession() as session:
        client = Client(
            api_key="YOUR_API_KEY_HERE",
            websession=session,
        )
        await client.login()
        await client.setup_devices()
        devices = client.get_devices()
        print(f"Found {len(devices)} device(s)\n")

        for serial, device in devices.items():
            await client.get_latest_data(serial)
            print(f"--- {device.device_name} ({serial}) ---")
            print(f"  Room: {device.room_name}")
            print(f"  Timezone: {device.timezone} (UTC{device.utc_offset})")
            print(f"  Timestamp: {device.timestamp}")
            print("  Sensors:")
            for field in device.SENSOR_FIELDS:
                attr = device._to_attr_name(field)
                value = getattr(device, attr)
                if value is not None:
                    print(f"    {attr}: {value}")
            print()


asyncio.run(main())
