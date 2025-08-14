import json, os, time
from uptime_kuma_api import UptimeKumaApi, MonitorType

URL = os.getenv("KUMA_URL", "http://uptime-kuma:3001")
USER = os.getenv("KUMA_USER", "admin")
PASS = os.getenv("KUMA_PASS", "")
CFG_PATH = os.getenv("MONITORS_JSON", "/app/monitors.json")

def as_type(t):
    return {"http": MonitorType.HTTP, "port": MonitorType.TCP_PORT}.get(t)

def upsert(api, m):
    name = m["name"]
    mtype = as_type(m["type"])
    if not mtype:
        print(f"- skip {name}: unsupported type {m.get('type')}")
        return
    existing = {mon["name"]: mon for mon in api.get_monitors()}
    if name in existing:
        mon_id = existing[name]["id"]
        print(f"- update {name}")
        if mtype == MonitorType.HTTP:
            api.edit_monitor(
                mon_id, type=mtype, name=name, url=m["url"],
                interval=m.get("interval", 60),
                retryInterval=m.get("retryInterval", m.get("interval", 60)),
                maxretries=m.get("maxretries", 0),
                timeout=m.get("timeout", 30),
                upsideDown=m.get("upsideDown", False),
                maxredirects=m.get("maxredirects", 10),
                accepted_statuscodes=m.get("accepted_statuscodes", ["200-299"]),
                method=m.get("method", "GET"),
                body=m.get("body"), headers=m.get("headers"),
                httpBodyEncoding=m.get("httpBodyEncoding", "json"),
                keyword=m.get("keyword"),
                invertKeyword=m.get("invertKeyword", False),
                ignoreTls=m.get("ignoreTls", False),
                proxyId=m.get("proxyId"),
                notificationIDList=m.get("notificationIDList", {}),
                tags=m.get("tags", []),
                active=m.get("active", True),
            )
        else:
            api.edit_monitor(
                mon_id, type=mtype, name=name,
                hostname=m["hostname"], port=m["port"],
                interval=m.get("interval", 60),
                retryInterval=m.get("retryInterval", m.get("interval", 60)),
                maxretries=m.get("maxretries", 0),
                timeout=m.get("timeout", 30),
                upsideDown=m.get("upsideDown", False),
                notificationIDList=m.get("notificationIDList", {}),
                tags=m.get("tags", []),
                active=m.get("active", True),
            )
    else:
        print(f"- create {name}")
        if mtype == MonitorType.HTTP:
            api.add_monitor(
                type=mtype, name=name, url=m["url"],
                interval=m.get("interval", 60),
                retryInterval=m.get("retryInterval", m.get("interval", 60)),
                maxretries=m.get("maxretries", 0),
                timeout=m.get("timeout", 30),
                upsideDown=m.get("upsideDown", False),
                maxredirects=m.get("maxredirects", 10),
                accepted_statuscodes=m.get("accepted_statuscodes", ["200-299"]),
                method=m.get("method", "GET"),
                body=m.get("body"), headers=m.get("headers"),
                httpBodyEncoding=m.get("httpBodyEncoding", "json"),
                keyword=m.get("keyword"),
                invertKeyword=m.get("invertKeyword", False),
                ignoreTls=m.get("ignoreTls", False),
                proxyId=m.get("proxyId"),
                notificationIDList=m.get("notificationIDList", {}),
                tags=m.get("tags", []),
                active=m.get("active", True),
            )
        else:
            api.add_monitor(
                type=mtype, name=name,
                hostname=m["hostname"], port=m["port"],
                interval=m.get("interval", 60),
                retryInterval=m.get("retryInterval", m.get("interval", 60)),
                maxretries=m.get("maxretries", 0),
                timeout=m.get("timeout", 30),
                upsideDown=m.get("upsideDown", False),
                notificationIDList=m.get("notificationIDList", {}),
                tags=m.get("tags", []),
                active=m.get("active", True),
            )

def main():
    # warten bis Login klappt
    for _ in range(60):
        try:
            api = UptimeKumaApi(URL)
            api.login(USER, PASS)
            break
        except Exception:
            time.sleep(2)
    else:
        raise RuntimeError("Login bei Uptime-Kuma fehlgeschlagen.")

    with open(CFG_PATH, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    for m in cfg.get("monitorList", []):
        upsert(api, m)

    api.logout()
    print("Seeding done.")

if __name__ == "__main__":
    main()
