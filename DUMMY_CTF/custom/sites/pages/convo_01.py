import reflex as rx
from website.unlock_settings import *
from website.auth_lib import AuthCookie
from website.engine.site import AbstractSiteBuilder
from website.engine.convo import PlayerConversationWidget, Player


class Konversation_01(AbstractSiteBuilder):
    def page(self) -> rx.Component:
        chapter="01"
        player_left = Player("Martin")       
        player_right = Player("Du")

        return rx.vstack(
        
            PlayerConversationWidget.create(
                chapter,
                player_left,
                player_right,
                [
                    player_right.say("So, ich wäre dann mal bereit für die technische Einweisung...", pose_left="nobody"),
                    player_right.say("Ah, da kommt ja jemand!", pose_left="shadow"),
                    player_left.say("Base Pose", pose_left=""),
                    player_left.say("Anger Pose", pose_left="anger"),
                    player_left.say("Fear Pose", pose_left="fear"),
                    player_left.say("Joy Pose", pose_left="joy"),
                    player_left.say("Sadness Pose", pose_left="sadness"),
                    player_left.say("Suprise Pose", pose_left="suprise"),
                    player_right.say("Verstanden...", pose_left=""),
                ],
            ),
       
            rx.image(
                src=f"/poses/player_{player_right.name.lower()}_{AuthCookie.get_player_path.lower()}.png",
                class_name="player_avatar",
                style=rx.style.Style({"right": "5vw"}),
                alt="Player Right"
            ),

        )

    def configure(self) -> None:
        self.page_title = "Dialog"
        self.url = "/char_01"
        self.is_standalone = True
        self.hide_sidebar = True
        self.background_class = "convo_background"
        self.auth_required = True
        self.unlock_day = unlock_always