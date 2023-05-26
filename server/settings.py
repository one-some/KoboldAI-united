import os
import json
from typing import Optional
from dataclasses import dataclass

import koboldai_settings
from server.formatting import kml
from server.kaivars import koboldai_vars
from modeling.inference_model import InferenceModel


@dataclass
class Setting:
    name: str
    kai_vars_name: Optional[str] = None
    alter_default_preset: Optional[bool] = False


# ==================================================================#
# ==================================================================#


def load_settings(model_name: str) -> None:
    """Read settings from client file JSON and send to koboldai_vars"""

    path = "settings/" + model_name.replace("/", "_") + ".v2_settings"
    if not os.path.exists(path):
        return

    with open(path, "r") as file:
        koboldai_vars._model_settings.from_json(file.read())


def load_model_settings(model: InferenceModel):
    """Allow the models to override some settings"""

    model.model_config

    config = {}

    try:
        config = model.config
    except AttributeError:
        for model_dir in [
            koboldai_vars.custmodpth,
            koboldai_vars.custmodpth.replace("/", "_"),
        ]:
            try:
                with open(os.path.join(model_dir, "config.json"), "r") as file:
                    config = json.load(file)
            except FileNotFoundError:
                pass

    koboldai_vars.default_preset = koboldai_settings.default_preset

    if koboldai_vars.model_type == "xglm" or config.get("compat", "j") == "fairseq_lm":
        koboldai_vars.newlinemode = "s"  # Default to </s> newline mode if using XGLM
    if koboldai_vars.model_type == "opt" or koboldai_vars.model_type == "bloom":
        koboldai_vars.newlinemode = "ns"  # Handle </s> but don't convert newlines if using Fairseq models that have newlines trained in them

    koboldai_vars.modelconfig = config

    # Simple settings
    for setting in [
        Setting("badwordsids"),
        Setting("nobreakmodel"),
        Setting("temp", alter_default_preset=True),
        Setting("top_p", alter_default_preset=True),
        Setting("top_k", alter_default_preset=True),
        Setting("tfs", alter_default_preset=True),
        Setting("typical", alter_default_preset=True),
        Setting("top_a", alter_default_preset=True),
        Setting("rep_pen", alter_default_preset=True),
        Setting("rep_pen_slope", alter_default_preset=True),
        Setting("rep_pen_range", alter_default_preset=True),
        Setting("adventure"),
        Setting("chatmode"),
        Setting("dynamicscan"),
        Setting("newlinemode"),
    ]:
        setattr(
            koboldai_vars, setting.kai_vars_name or setting.name, config[setting.name]
        )
        if setting.alter_default_preset:
            koboldai_vars.default_preset[setting.name] = config[setting.name]

    # More complicated settings have their own logic

    if "sampler_order" in config:
        sampler_order = config["sampler_order"]
        if len(sampler_order) < 7:
            sampler_order = [6] + sampler_order
        koboldai_vars.sampler_order = sampler_order

    if "formatoptns" in config:
        for setting in [
            "frmttriminc",
            "frmtrmblln",
            "frmtrmspch",
            "frmtadsnsp",
            "singleline",
        ]:
            if setting in config["formatoptns"]:
                setattr(koboldai_vars, setting, config["formatoptns"][setting])

    if "welcome" in config:
        koboldai_vars.welcome = (
            kml(config["welcome"])
            if config["welcome"] != False
            else koboldai_vars.welcome_default
        )

    if "newlinemode" in config:
        koboldai_vars.newlinemode = config["newlinemode"]

    if "antemplate" in config:
        koboldai_vars.setauthornotetemplate = config["antemplate"]
        if not koboldai_vars.gamestarted:
            koboldai_vars.authornotetemplate = koboldai_vars.setauthornotetemplate


def ui1_refresh_settings() -> None:
    """Sends the current generator settings to the Game Menu"""
    # Suppress toggle change events while loading state
    socketio.emit(
        "from_server",
        {"cmd": "allowtoggle", "data": False},
        broadcast=True,
        room="UI_1",
    )

    if koboldai_vars.model != "InferKit":
        socketio.emit(
            "from_server",
            {"cmd": "updatetemp", "data": koboldai_vars.temp},
            broadcast=True,
            room="UI_1",
        )
        socketio.emit(
            "from_server",
            {"cmd": "updatetopp", "data": koboldai_vars.top_p},
            broadcast=True,
            room="UI_1",
        )
        socketio.emit(
            "from_server",
            {"cmd": "updatetopk", "data": koboldai_vars.top_k},
            broadcast=True,
            room="UI_1",
        )
        socketio.emit(
            "from_server",
            {"cmd": "updatetfs", "data": koboldai_vars.tfs},
            broadcast=True,
            room="UI_1",
        )
        socketio.emit(
            "from_server",
            {"cmd": "updatetypical", "data": koboldai_vars.typical},
            broadcast=True,
            room="UI_1",
        )
        socketio.emit(
            "from_server",
            {"cmd": "updatetopa", "data": koboldai_vars.top_a},
            broadcast=True,
            room="UI_1",
        )
        socketio.emit(
            "from_server",
            {"cmd": "updatereppen", "data": koboldai_vars.rep_pen},
            broadcast=True,
            room="UI_1",
        )
        socketio.emit(
            "from_server",
            {"cmd": "updatereppenslope", "data": koboldai_vars.rep_pen_slope},
            broadcast=True,
            room="UI_1",
        )
        socketio.emit(
            "from_server",
            {"cmd": "updatereppenrange", "data": koboldai_vars.rep_pen_range},
            broadcast=True,
            room="UI_1",
        )
        socketio.emit(
            "from_server",
            {"cmd": "updateoutlen", "data": koboldai_vars.genamt},
            broadcast=True,
            room="UI_1",
        )
        socketio.emit(
            "from_server",
            {"cmd": "updatetknmax", "data": koboldai_vars.max_length},
            broadcast=True,
            room="UI_1",
        )
        socketio.emit(
            "from_server",
            {"cmd": "updatenumseq", "data": koboldai_vars.numseqs},
            broadcast=True,
            room="UI_1",
        )
    else:
        socketio.emit(
            "from_server",
            {"cmd": "updatetemp", "data": koboldai_vars.temp},
            broadcast=True,
            room="UI_1",
        )
        socketio.emit(
            "from_server",
            {"cmd": "updatetopp", "data": koboldai_vars.top_p},
            broadcast=True,
            room="UI_1",
        )
        socketio.emit(
            "from_server",
            {"cmd": "updateikgen", "data": koboldai_vars.ikgen},
            broadcast=True,
            room="UI_1",
        )

    socketio.emit(
        "from_server",
        {"cmd": "updateanotedepth", "data": koboldai_vars.andepth},
        broadcast=True,
        room="UI_1",
    )
    socketio.emit(
        "from_server",
        {"cmd": "updatewidepth", "data": koboldai_vars.widepth},
        broadcast=True,
        room="UI_1",
    )
    socketio.emit(
        "from_server",
        {"cmd": "updateuseprompt", "data": koboldai_vars.useprompt},
        broadcast=True,
        room="UI_1",
    )
    socketio.emit(
        "from_server",
        {"cmd": "updateadventure", "data": koboldai_vars.adventure},
        broadcast=True,
        room="UI_1",
    )
    socketio.emit(
        "from_server",
        {"cmd": "updatechatmode", "data": koboldai_vars.chatmode},
        broadcast=True,
        room="UI_1",
    )
    socketio.emit(
        "from_server",
        {"cmd": "updatedynamicscan", "data": koboldai_vars.dynamicscan},
        broadcast=True,
        room="UI_1",
    )
    socketio.emit(
        "from_server",
        {"cmd": "updateautosave", "data": koboldai_vars.autosave},
        broadcast=True,
        room="UI_1",
    )
    socketio.emit(
        "from_server",
        {"cmd": "updatenopromptgen", "data": koboldai_vars.nopromptgen},
        broadcast=True,
        room="UI_1",
    )
    socketio.emit(
        "from_server",
        {"cmd": "updaterngpersist", "data": koboldai_vars.rngpersist},
        broadcast=True,
        room="UI_1",
    )
    socketio.emit(
        "from_server",
        {"cmd": "updatenogenmod", "data": koboldai_vars.nogenmod},
        broadcast=True,
        room="UI_1",
    )
    socketio.emit(
        "from_server",
        {"cmd": "updatefulldeterminism", "data": koboldai_vars.full_determinism},
        broadcast=True,
        room="UI_1",
    )

    socketio.emit(
        "from_server",
        {"cmd": "updatefrmttriminc", "data": koboldai_vars.frmttriminc},
        broadcast=True,
        room="UI_1",
    )
    socketio.emit(
        "from_server",
        {"cmd": "updatefrmtrmblln", "data": koboldai_vars.frmtrmblln},
        broadcast=True,
        room="UI_1",
    )
    socketio.emit(
        "from_server",
        {"cmd": "updatefrmtrmspch", "data": koboldai_vars.frmtrmspch},
        broadcast=True,
        room="UI_1",
    )
    socketio.emit(
        "from_server",
        {"cmd": "updatefrmtadsnsp", "data": koboldai_vars.frmtadsnsp},
        broadcast=True,
        room="UI_1",
    )
    socketio.emit(
        "from_server",
        {"cmd": "updatesingleline", "data": koboldai_vars.singleline},
        broadcast=True,
        room="UI_1",
    )
    socketio.emit(
        "from_server",
        {"cmd": "updateoutputstreaming", "data": koboldai_vars.output_streaming},
        broadcast=True,
        room="UI_1",
    )
    socketio.emit(
        "from_server",
        {"cmd": "updateshowbudget", "data": koboldai_vars.show_budget},
        broadcast=True,
        room="UI_1",
    )
    socketio.emit(
        "from_server",
        {"cmd": "updateshowprobs", "data": koboldai_vars.show_probs},
        broadcast=True,
        room="UI_1",
    )
    socketio.emit(
        "from_server",
        {"cmd": "updatealt_text_gen", "data": koboldai_vars.alt_gen},
        broadcast=True,
        room="UI_1",
    )
    socketio.emit(
        "from_server",
        {"cmd": "updatealt_multi_gen", "data": koboldai_vars.alt_multi_gen},
        broadcast=True,
        room="UI_1",
    )

    # Allow toggle events again
    socketio.emit(
        "from_server", {"cmd": "allowtoggle", "data": True}, broadcast=True, room="UI_1"
    )
