from unittest.mock import Mock, patch
import requests
import monitor


def test_delivery_uses_timeout():
    response = Mock()
    response.json.return_value = {"ok": True}
    with patch.object(monitor.requests, "post", return_value=response) as post:
        assert monitor.send_alert("test") is True
        assert post.call_args.kwargs["timeout"] == (3, 10)
        response.raise_for_status.assert_called_once()


def test_delivery_failure_is_contained():
    with patch.object(monitor.requests, "post", side_effect=requests.Timeout("sensitive URL")):
        assert monitor.send_alert("test") is False


def test_failed_delivery_retries_and_recovery_follows_success():
    state = {}
    with patch.object(monitor, "send_alert", side_effect=[False, True, True]) as send:
        monitor.notify_changes({"CPU": 99}, state, 0)
        monitor.notify_changes({"CPU": 99}, state, 60)
        monitor.notify_changes({"CPU": 99}, state, 120)
        assert send.call_count == 2
        monitor.notify_changes({"CPU": 1}, state, 180)
        assert send.call_count == 3
        assert state["CPU"]["active"] is False


def test_disk_path_is_explicit():
    with patch.object(monitor.psutil, "cpu_percent", return_value=5), \
         patch.object(monitor.psutil, "virtual_memory", return_value=Mock(percent=10)), \
         patch.object(monitor.psutil, "disk_usage", return_value=Mock(percent=20)) as disk, \
         patch.object(monitor, "DISK_PATH", "/host/rootfs"):
        assert monitor.check_metrics()["DISK"] == 20
        disk.assert_called_once_with("/host/rootfs")
