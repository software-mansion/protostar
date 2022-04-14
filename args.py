def test(*events):
    for event in events:
        print(event)


test({"event_name": "foo"}, "bar")
