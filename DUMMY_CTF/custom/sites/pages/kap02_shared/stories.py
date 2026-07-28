"""
Narrative intros for Kapitel 02 — short spy/interception stories.

Each story gives an intuitive, non-mathematical picture of the mechanism
before the technical part begins, so that even students who struggle with
the maths already grasp the idea.

Style: Sie-Anrede, spy/interception scenario, self-contained, no maths.
"""

import reflex as rx


def _story_box(title: str, body_md: str, color: str) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.icon("book-open", size=18, color=color),
                rx.text(rx.text.strong(title), font_size="1.15em", color=color),
                align_items="center", spacing="2",
            ),
            rx.markdown(body_md),
            spacing="2", align_items="start",
        ),
        style={
            "maxWidth": "1200px", "width": "100%", "margin": "18px auto",
            "padding": "22px 25px", "borderRadius": "16px",
            "background": "rgba(255, 236, 200, 0.06)",
            "border": "1px solid rgba(255, 220, 160, 0.16)",
            "boxSizing": "border-box", "borderLeft": f"4px solid {color}",
            "fontStyle": "italic",
        },
    )


# ---------------------------------------------------------------------------
# Story: how Diffie-Hellman works (intro to the whole chapter)
# ---------------------------------------------------------------------------
def dh_intro(color: str = "#EF9F27") -> rx.Component:
    return _story_box(
        "Die Geschichte: Ein Geheimnis über eine offene Leitung",
        r"""
Stellen Sie sich vor: Zwei Agenten, **Anna** und **Bob**, müssen sich auf ein
gemeinsames Codewort einigen. Das Problem: ihr einziger Kommunikationskanal ist
ein Funkgerät, und **jeder hört mit**. Sie können das Codewort also nicht einfach
aussprechen.

Ihr Trick ist verblüffend. Jeder von beiden denkt sich eine geheime Zahl aus, die
er **niemandem** verrät. Über den Funk tauschen sie nur *Mischungen* aus — Werte,
die aus ihrer Geheimzahl berechnet wurden, aus denen man die Geheimzahl aber nicht
zurückrechnen kann. Anna nimmt Bobs Mischung und verrührt sie mit ihrer Geheimzahl;
Bob nimmt Annas Mischung und verrührt sie mit seiner. Wie durch Magie erhalten
**beide dasselbe Ergebnis**, ihr gemeinsames Codewort.

Die Lauscherin am Funkgerät hört alle Mischungen mit. Doch ohne eine der beiden
Geheimzahlen kann sie das Codewort nicht nachbauen. Das ist Diffie-Hellman: ein
gemeinsames Geheimnis, das nie über die Leitung ging.

*In diesem Kapitel sind **Sie** die Lauscherin und Sie werden lernen, warum das
Verfahren manchmal doch zu knacken ist.*
        """,
        color,
    )


# ---------------------------------------------------------------------------
# Story: Challenge 1 — small parameters
# ---------------------------------------------------------------------------
def challenge_1(color: str = "#EF9F27") -> rx.Component:
    return _story_box(
        "Die Geschichte: Ein zu kleines Zahlenschloss",
        r"""
Sie haben einen Funkspruch abgefangen. Zwei Amateure haben Diffie-Hellman
benutzt aber sie haben einen entscheidenden Fehler gemacht: Die Zahlen, mit
denen sie rechnen, sind **viel zu klein**.

Stellen Sie sich ein Fahrradschloss mit nur drei Ziffern vor. Ein geübter Dieb
probiert einfach alle 1000 Kombinationen durch - in wenigen Minuten ist es offen.
Genau so ist es hier: Der geheime Wert ist so klein, dass Sie ihn schlicht
**durchprobieren** können, bis es passt.

Ihre Aufgabe: Knacken Sie das kleine Schloss, rekonstruieren Sie das gemeinsame
Geheimnis und entschlüsseln Sie die abgefangene Nachricht.
        """,
        color,
    )


# ---------------------------------------------------------------------------
# Story: Challenge 2 — smooth order
# ---------------------------------------------------------------------------
def challenge_2(color: str = "#EF9F27") -> rx.Component:
    return _story_box(
        "Die Geschichte: Der Tresor mit den vielen kleinen Schlössern",
        r"""
Diesmal waren Ihre Zielpersonen vorsichtiger. Die Zahlen sind **riesig** -
Durchprobieren ist völlig aussichtslos. Auf den ersten Blick sieht der
abgefangene Austausch bombensicher aus.

Doch es gibt einen Haken. Stellen Sie sich einen schweren Tresor vor, dessen
Tür nicht durch **ein** großes Schloss gesichert ist, sondern durch **viele
kleine** nebeneinander. Jedes einzelne davon ist mit etwas Geduld zu knacken -
und wer alle kleinen Schlösser öffnet, hat den ganzen Tresor offen.

Genau diese Schwäche steckt hier in den Zahlen: Die geheime Struktur zerfällt
in lauter kleine, handhabbare Teile. Ihre Aufgabe: zerlegen Sie den Tresor in
seine kleinen Schlösser, knacken Sie jedes einzeln und setzen Sie das Ergebnis
zusammen.
        """,
        color,
    )


# ---------------------------------------------------------------------------
# Story: Challenge 3 — the trap
# ---------------------------------------------------------------------------
def challenge_3(color: str = "#EF9F27") -> rx.Component:
    return _story_box(
        "Die Geschichte: Die trügerische Festung",
        r"""
Ihre letzte Zielperson hat aus den Fehlern der anderen gelernt - glaubt sie
zumindest. Die Zahl ist **gewaltig**, größer als alles zuvor. Eine wahre
Festung. Jeder normale Angreifer würde hier aufgeben.

Aber Sie schauen genauer hin. Hinter der imposanten Mauer verbirgt sich
dieselbe alte Schwäche wie zuvor - nur ist sie diesmal **teilweise** hinter
einem echten, unknackbaren Riegel versteckt. Der Clou: Sie **brauchen** diesen
Riegel gar nicht zu knacken. Das Geheimnis, das Sie suchen, ist klein genug,
dass die *schwachen* Teile der Festung völlig ausreichen, um es zu bergen.

Die Größe der Mauer war reine Einschüchterung. Bergen Sie die letzte Nachricht
und beweisen Sie, dass groß nicht gleich sicher bedeutet.
        """,
        color,
    )


# ---------------------------------------------------------------------------
# Story: Challenge 4 — weak generator (small subgroup)
# ---------------------------------------------------------------------------
def challenge_4(color: str = "#EF9F27") -> rx.Component:
    return _story_box(
        "Die Geschichte: Der Schlüsseldienst mit dem Ladenhüter",
        r"""
Ihre neue Zielperson hat diesmal eine **riesige** Primzahl gewählt - alles sieht
tadellos aus. Doch sie hat einen unscheinbaren Fehler gemacht: Sie hat den
**Erzeuger** schlampig gewählt.

Stellen Sie sich einen Schlüsseldienst vor, der mit einem teuren Hochsicherheits-
schloss wirbt. Was der Kunde nicht weiß: Der Dienst fertigt die Schlüssel aus
einer winzigen Vorlage - es gibt in Wirklichkeit nur ein paar Tausend
verschiedene Schlüssel. Das Schloss selbst mag kompliziert sein, aber wer alle
paar Tausend Möglichkeiten durchgeht, ist trotzdem schnell drin.

Genau das ist hier passiert: Der Erzeuger deckt nur einen **winzigen Teil** des
riesigen Zahlenraums ab. Die imposante Größe der Primzahl ist bedeutungslos -
das Geheimnis lebt in einem kleinen Käfig. Bergen Sie es.
        """,
        color,
    )


# ---------------------------------------------------------------------------
# Story: Challenge 5 — Logjam (export-grade)
# ---------------------------------------------------------------------------
def challenge_5(color: str = "#EF9F27") -> rx.Component:
    return _story_box(
        "Die Geschichte: Das absichtlich schwache Schloss",
        r"""
Diese Nachricht ist besonders. Sie stammt aus einem System, das noch mit einem
**absichtlich geschwächten** Verfahren arbeitet - einem Relikt aus einer Zeit,
in der starke Verschlüsselung gesetzlich beschränkt war und Systeme mit
bewusst kleinen „Export-Schlüsseln" ausgeliefert wurden.

Das erinnert Sie an etwas: Im vorigen Kapitel haben Sie mit FREAK bereits eine
solche Export-Schwäche ausgenutzt - dort ging es um zu kleine RSA-Module. Hier
ist es das Gegenstück auf der Diffie-Hellman-Seite: eine standardisierte, aber
viel zu schwache Gruppe, wie beim realen **Logjam**-Angriff.

Das Tückische: Dieselbe schwache Gruppe wird von tausenden Systemen benutzt.
Wer sie einmal knackt, knackt sie für alle. Bergen Sie die Nachricht und
schließen Sie den Bogen zum FREAK-Angriff.
        """,
        color,
    )


# ---------------------------------------------------------------------------
# Story: Challenge 6 — Man-in-the-Middle
# ---------------------------------------------------------------------------
def challenge_6(color: str = "#EF9F27") -> rx.Component:
    return _story_box(
        "Die Geschichte: Die Frau in der Mitte",
        r"""
Bisher waren Sie eine stille Lauscherin - Sie haben mitgehört und im
Nachhinein entschlüsselt. Diesmal gehen Sie einen entscheidenden Schritt
weiter: Sie greifen **aktiv** ein.

Anna will mit Bob ein Geheimnis vereinbaren. Doch Sie sitzen unbemerkt
zwischen den beiden. Als Anna ihren Wert an Bob schickt, fangen Sie ihn ab
und schicken Anna **Ihren eigenen** zurück - Anna hält ihn für Bobs. Dasselbe
Spiel in die andere Richtung mit Bob. Von nun an führen Sie in Wahrheit
**zwei** Gespräche: eines mit Anna, eines mit Bob. Beide glauben, direkt
miteinander zu reden.

Das Verblüffende: Die Zahlen sind diesmal **perfekt gewählt** - der diskrete
Logarithmus ist hier aussichtslos, kein noch so guter Angriff bricht ihn. Und
trotzdem lesen Sie jedes Wort. Denn Sie müssen gar nichts brechen: Sie kennen
Ihre eigenen Geheimnisse und damit **beide** Sitzungsschlüssel.

Ihre Aufgabe: Weisen Sie den Angriff nach, entschlüsseln Sie beide Richtungen
und setzen Sie die Nachricht zusammen. Und verstehen Sie, warum selbst perfekte
Mathematik nichts nützt, wenn niemand prüft, **mit wem** er eigentlich spricht.
        """,
        color,
    )


# ---------------------------------------------------------------------------
# Story: Challenge 7 — ECDH intro (elliptic curves)
# ---------------------------------------------------------------------------
def challenge_7(color: str = "#EF9F27") -> rx.Component:
    return _story_box(
        "Die Geschichte: Ein neues Spielfeld",
        r"""
Bislang spielte sich alles auf der vertrauten Zahlengeraden ab - Reste modulo
einer Primzahl. Doch Ihre Zielpersonen haben aufgerüstet: Sie rechnen jetzt auf
einer **elliptischen Kurve**. Statt Zahlen zu multiplizieren, „addieren" sie
Punkte auf einer geschwungenen Kurve.

Erschrecken Sie nicht - im Kern ist es dasselbe Spiel. Auch hier gibt es einen
Startpunkt, ein Geheimnis (wie oft man den Startpunkt mit sich selbst
„verkettet"), und einen öffentlichen Punkt, der daraus entsteht. Und wie zuvor
gilt: Aus dem öffentlichen Punkt das Geheimnis zurückzurechnen ist **schwer** -
das ist das elliptische Gegenstück zum diskreten Logarithmus.

Ihre heutigen Amateure haben jedoch denselben klassischen Fehler gemacht wie
ganz am Anfang: Die Kurve, die sie gewählt haben, ist **zu klein**. Der Raum der
möglichen Geheimnisse ist überschaubar - und was überschaubar ist, lässt sich
durchsuchen. Betreten Sie das neue Spielfeld, lernen Sie, auf der Kurve zu
rechnen, und bergen Sie die Nachricht.
        """,
        color,
    )


# ---------------------------------------------------------------------------
# Story: Challenge 8 — Invalid Curve Attack
# ---------------------------------------------------------------------------
def challenge_8(color: str = "#EF9F27") -> rx.Component:
    return _story_box(
        "Die Geschichte: Der Türsteher, der die Ausweise nicht liest",
        r"""
Diesmal ist Ihr Gegner ein Profi. Bob benutzt eine **große, sichere** Kurve -
den elliptischen Log zu brechen ist völlig aussichtslos. Und doch hat er eine
Achillesferse.

Stellen Sie sich einen Türsteher vor, der jeden Ausweis abstempelt, den man ihm
reicht - ohne je zu prüfen, ob der Ausweis überhaupt echt ist. Genau das tut
Bob: Wenn ihm jemand einen Punkt schickt, rechnet er brav mit seinem geheimen
Schlüssel darauf - **ohne zu prüfen, ob der Punkt wirklich auf seiner Kurve
liegt**.

Sie nutzen das schamlos aus. Sie schicken Bob Punkte, die auf ganz **anderen,
schwachen Kurven** leben. Aus seinen Antworten lesen Sie jedes Mal ein kleines
Bruchstück seines Geheimnisses ab. Stück für Stück, Kurve für Kurve - und am
Ende setzen Sie die Bruchstücke zum vollständigen Schlüssel zusammen. Bergen Sie
Bobs geheimen Schlüssel und entschlüsseln Sie seine Nachricht.
        """,
        color,
    )


# ---------------------------------------------------------------------------
# Story: Challenge 9 — ElGamal reused nonce
# ---------------------------------------------------------------------------
def challenge_9(color: str = "#EF9F27") -> rx.Component:
    return _story_box(
        "Die Geschichte: Zweimal derselbe Würfel",
        r"""
Sie haben zwei verschlüsselte Nachrichten desselben Absenders abgefangen. Das
Verfahren (ElGamal) ist grundsolide - bei jeder Verschlüsselung soll ein
**frischer Zufallswert** gewürfelt werden, damit selbst zwei gleiche Nachrichten
völlig verschieden aussehen.

Doch Ihr Absender war bequem. Er hat den Würfel **nur einmal geworfen** und
denselben Zufallswert für beide Nachrichten benutzt. Ein winziger Fehler mit
fataler Wirkung: Von der ersten Nachricht kennen Sie den Klartext (es ist ein
Standard-Header). Weil der Zufallswert identisch war, hebt er sich beim
Vergleich beider Chiffrate **heraus** - und die zweite, geheime Nachricht fällt
Ihnen in den Schoß, ganz ohne den diskreten Logarithmus zu knacken.

Finden Sie das verräterische Zeichen für den wiederverwendeten Würfel und bergen
Sie die geheime Nachricht.
        """,
        color,
    )


# ---------------------------------------------------------------------------
# Story: Challenge 10 — DSA reused nonce (the finale)
# ---------------------------------------------------------------------------
def challenge_10(color: str = "#EF9F27") -> rx.Component:
    return _story_box(
        "Die Geschichte: Der Fehler, der eine Spielkonsole knackte",
        r"""
Das große Finale. Diesmal geht es nicht um Verschlüsselung, sondern um
**Unterschriften**. Mit einem geheimen Schlüssel signiert man Nachrichten; jeder
kann mit dem öffentlichen Schlüssel prüfen, dass sie echt sind. Der private
Schlüssel darf **niemals** herauskommen - sonst kann der Angreifer beliebige
Fälschungen unterschreiben.

Auch hier braucht jede Signatur einen frischen Zufallswert. Und auch hier hat
jemand geschlampt: Zwei Signaturen wurden mit **demselben** Zufallswert
erzeugt. Das ist kein theoretisches Problem - genau dieser Fehler hat 2010 die
Sicherheit einer ganzen **Spielkonsole** (PlayStation 3) zerstört und später
echtes Geld aus **Bitcoin-Wallets** fließen lassen.

Aus zwei Signaturen mit gleichem Zufallswert lässt sich der geheime Schlüssel
direkt **ausrechnen**. Holen Sie sich den privaten Schlüssel, entschlüsseln Sie
die letzte Nachricht - und schließen Sie das Kapitel ab.
        """,
        color,
    )
