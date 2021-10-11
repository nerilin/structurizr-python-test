
import logging

from structurizr import Workspace
from structurizr.model import Tags
from structurizr.view import ElementStyle, Shape, RelationshipStyle, Border


class NewTags(Tags):
    USAGE = 'Usage'
    MODIFICATION = 'Modification'


def main() -> Workspace:
    workspace = Workspace(
        name='New brand company',
        description='Пример workspace',
    )

    model = workspace.model

    client = model.add_person(
        name='Держатель карты',
        description='Физическое лицо, держатель карты'
    )

    merchant = model.add_software_system(
        name='Мерчант',
        description='Сайт мерчанта/Фасилитатора'
    )

    acquiring = model.add_software_system(
        name='Эквайринг',
        description='Система эквайринга'
    )

    mps = model.add_software_system(
        name='МПС',
        description='Международная платежная система'
    )

    mpi = model.add_software_system(
        name='MPI'
    )

    issuer = model.add_software_system(
        name='Банк-эмитент',
        description='Банк, выпустивший карту'
    )

    client.uses(destination=merchant, description='Ввод данных карты')
    client.uses(destination=issuer, description='Ввод OTP')

    merchant.uses(destination=acquiring, description='Платежный протокол')
    merchant.uses(destination=acquiring, description='Протокол управления привязками')

    acquiring.uses(destination=mps, description='Протокол авторизации')
    acquiring.uses(destination=mpi, description='Протокол 3DS')

    mpi.uses(destination=issuer, description='Протокол 3DS')

    mps.uses(destination=issuer, description='Протокол авторизации')

    views = workspace.views
    acquiring_context_view = views.create_system_context_view(
        software_system=acquiring,
        key='Acquiring context',
        description='Контекстная схема эквайринга'
    )

    acquiring_context_view.add(client)
    acquiring_context_view.add(acquiring)
    acquiring_context_view.add(merchant)
    acquiring_context_view.add(mps)
    acquiring_context_view.add(mpi)
    acquiring_context_view.add(issuer)

    redbox = acquiring.add_container(name='RedBox')
    redbox_dm = acquiring.add_container(name='Redbox DecisionMaker')
    card_binder = acquiring.add_container(name='CardBinder')

    merchant.uses(destination=redbox, description='Создание заказа')
    merchant.uses(destination=redbox, description='Подтверждение 3DS')

    redbox.uses(destination=redbox_dm, description='Запрос решения о проведении операции')
    redbox.uses(destination=card_binder, description='Запрос данных карты по привязке').tags.add(NewTags.MODIFICATION)
    redbox.uses(destination=mpi, description='Запрос вовлеченности в 3DS')
    redbox.uses(destination=mpi, description='Запрос прохождения 3DS')
    redbox.uses(destination=mps, description='Запрос авторизации')

    payment_view = views.create_container_view(
        software_system=acquiring,
        key='Acquiring payments decomposition',
        description='Декомпозиция приема платежей'
    )

    payment_view.add(client)
    payment_view.add(merchant)
    payment_view.add(redbox)
    payment_view.add(redbox_dm)
    payment_view.add(card_binder)
    payment_view.add(mpi)
    payment_view.add(mps)

    set_styles(views)
    return workspace


def set_styles(views):
    styles = views.configuration.styles
    styles.add(ElementStyle(tag=Tags.ELEMENT, color='#ffffff', font_size=34))
    styles.add(ElementStyle(tag='Risk System', background='#550000', color='#ffffff'))
    styles.add(
        ElementStyle(
            tag=Tags.SOFTWARE_SYSTEM,
            width=650,
            height=400,
            background='#801515',
            shape=Shape.RoundedBox,
        )
    )
    styles.add(
        ElementStyle(
            tag=Tags.PERSON, width=550, background='#d46a6a', shape=Shape.Person
        )
    )
    styles.add(
        RelationshipStyle(
            tag=Tags.RELATIONSHIP, thickness=4, dashed=False, font_size=32, width=400
        )
    )
    styles.add(RelationshipStyle(tag=Tags.SYNCHRONOUS, dashed=False))
    styles.add(RelationshipStyle(tag=Tags.ASYNCHRONOUS, dashed=True))
    styles.add(ElementStyle(tag=NewTags.MODIFICATION, opacity=30, border=Border.Dashed))
    styles.add(RelationshipStyle(tag=NewTags.MODIFICATION, opacity=30, dashed=True))


if __name__ == '__main__':
    logging.basicConfig(level='INFO')
    space = main()

    try:
        with open('workspace.json') as f:
            old_space = Workspace.loads(f.read())
            space.views.copy_layout_information_from(old_space.views)
    except:
        pass

    with open('workspace.json', 'w') as f:
        f.write(space.dumps());
