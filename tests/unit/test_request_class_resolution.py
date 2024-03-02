from typing import Type, Union

import pytest

from litestar import Controller, HttpMethod, Litestar, Request, Router, get

RouterRequest: Type[Request] = type("RouterRequest", (Request,), {})
ControllerRequest: Type[Request] = type("ControllerRequest", (Request,), {})
AppRequest: Type[Request] = type("AppRequest", (Request,), {})
HandlerRequest: Type[Request] = type("HandlerRequest", (Request,), {})


@pytest.mark.parametrize(
    "handler_request_class, controller_request_class, router_request_class, app_request_class, has_default_app_class, expected",
    (
        (HandlerRequest, ControllerRequest, RouterRequest, AppRequest, True, HandlerRequest),
        (None, ControllerRequest, RouterRequest, AppRequest, True, ControllerRequest),
        (None, None, RouterRequest, AppRequest, True, RouterRequest),
        (None, None, None, AppRequest, True, AppRequest),
        (None, None, None, None, True, Request),
        (None, None, None, None, False, Request),
    ),
    ids=(
        "Custom class for all layers",
        "Custom class for all above handler layer",
        "Custom class for all above controller layer",
        "Custom class for all above router layer",
        "No custom class for layers",
        "No default class in app",
    ),
)
def test_request_class_resolution_of_layers(
    handler_request_class: Union[Type[Request], None],
    controller_request_class: Union[Type[Request], None],
    router_request_class: Union[Type[Request], None],
    app_request_class: Union[Type[Request], None],
    has_default_app_class: bool,
    expected: Type[Request],
) -> None:
    class MyController(Controller):
        @get()
        def handler(self, request: Request) -> None:
            assert type(request) is expected

    if controller_request_class:
        MyController.request_class = ControllerRequest

    router = Router(path="/", route_handlers=[MyController])

    if router_request_class:
        router.request_class = router_request_class

    app = Litestar(route_handlers=[router])

    if app_request_class or not has_default_app_class:
        app.request_class = app_request_class  # type: ignore

    route_handler, _ = app.routes[0].route_handler_map[HttpMethod.GET]  # type: ignore

    if handler_request_class:
        route_handler.request_class = handler_request_class

    request_class = route_handler.resolve_request_class()
    assert request_class is expected
