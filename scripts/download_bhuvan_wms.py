import urllib.request
import time

url = "https://bhuvan-vec2.nrsc.gov.in/bhuvan/sisdpv2/wms?service=WMS&request=GetCapabilities"

output = r".\data\processed\bhuvan_wms_capabilities.xml"

for attempt in range(1, 6):

    print(f"Attempt {attempt}/5...")

    try:
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        response = urllib.request.urlopen(request, timeout=60)

        chunks = []

        while True:
            chunk = response.read(65536)

            if not chunk:
                break

            chunks.append(chunk)

        data = b"".join(chunks).decode("utf-8", "ignore")

        print("Downloaded bytes:", len(data))

        if len(data) < 1000000:
            print("Response appears incomplete. Retrying...")
            time.sleep(2)
            continue

        with open(output, "w", encoding="utf-8") as f:
            f.write(data)

        print("Successfully saved:", output)
        print("Total characters:", len(data))
        break

    except Exception as e:
        print("Error:", repr(e))
        time.sleep(2)

else:
    print("Could not download the complete capabilities document.")

