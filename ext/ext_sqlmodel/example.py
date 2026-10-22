import asyncio

from sqlmodel import Field, SQLModel, Relationship, select
from sqlalchemy.orm import selectinload
from sqlalchemy.util import greenlet_spawn

from config.main import local_configs
from core.context import ctx


class Team(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    headquarters: str

    heroes: list["Hero"] = Relationship(back_populates="team", passive_deletes="all")  # , cascade_delete=True)


class HeroBase(SQLModel):
    name: str = Field(index=True)
    secret_name: str
    age: int | None = Field(default=None, index=True)

    team_id: int | None = Field(default=None, foreign_key="team.id")


class Hero(HeroBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    team: Team | None = Relationship(back_populates="heroes")


async def actions():
    async with local_configs.extensions.rdb_user_center.instance as session:
        team_preventers = Team(name="Preventers", headquarters="Sharp Tower")
        team_z_force = Team(name="Z-Force", headquarters="Sister Margaret's Bar")
        session.add(team_preventers)
        session.add(team_z_force)
        await session.commit()

        # hero_deadpond = Hero(
        #     name="Deadpond", secret_name="Dive Wilson", team_id=team_z_force.id
        # )
        hero_deadpond = Hero(name="Deadpond", secret_name="Dive Wilson", team=team_z_force)
        hero_rusty_man = Hero(
            name="Rusty-Man",
            secret_name="Tommy Sharp",
            age=48,
            team=team_preventers,
        )
        hero_spider_boy = Hero(name="Spider-Boy", secret_name="Pedro Parqueador")
        session.add(hero_deadpond)
        session.add(hero_rusty_man)
        session.add(hero_spider_boy)
        await session.commit()

        await session.refresh(hero_deadpond)
        await session.refresh(hero_rusty_man)
        await session.refresh(hero_spider_boy)

        print("Created hero:", hero_deadpond)
        print("Created hero:", hero_rusty_man)
        print("Created hero:", hero_spider_boy)

        statement = select(Hero, Team).where(Hero.team_id == Team.id)
        statement = select(Hero, Team).join(Team, isouter=True)
        results = await session.execute(statement)
        rs = results.all()
        for hero, team in rs:
            print(f"Hero: {hero.name}, Team: {team.name if team else 'None'}")

        select(Hero).join(Team).where(Team.name == "Preventers")
        results = await session.execute(statement)
        for hero in results.scalars().all():
            print("Preventer Hero:", hero)

        statement = select(Hero, Team).join(Team).where(Team.name == "Preventers")
        results = await session.execute(statement)
        for hero, team in results.all():
            print("Preventer Hero:", hero, "Team:", team)

        statement = select(Hero).where(Hero.name == "Deadpond")
        result = await session.execute(statement)
        hero_spider_boy = result.scalars().first()
        print("Spider-Boy's team again:", hero_spider_boy.team if hero_spider_boy else "")

        statement = select(Team).where(Team.name == "Preventers").options(selectinload(Team.heroes))  # type: ignore
        result = await session.execute(statement)
        team_preventers = result.scalars().one()

        print("Preventers heroes:", team_preventers.heroes)

        statement = select(Team).where(Team.name == "Preventers")
        team = (await session.execute(statement)).scalars().one()
        await greenlet_spawn(team.heroes.clear)
        await session.delete(team)
        await session.commit()
        print("Deleted team:", team)


async def create_all():
    async with local_configs.extensions.rdb_user_center.engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)


async def main():
    async with ctx():
        await create_all()
        await actions()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    # directly run: aiomysql close connection will raise event loop close error
