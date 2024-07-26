from sqlalchemy import TIMESTAMP, ForeignKey, Integer, String, Text, Date, Index
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship

Base = declarative_base()


class Rfc(Base):
    __tablename__ = 'rfc'

    num: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String)
    published_at: Mapped[Date] = mapped_column(Date, index=True)

    authors: Mapped[list["Author"]] = relationship(
        "Author", back_populates="rfc", cascade="all, delete-orphan"
    )
    sections: Mapped[list["RfcSection"]] = relationship(
        "RfcSection", back_populates="rfc", cascade="all, delete-orphan"
    )
    token_positions: Mapped[list["TokenPosition"]] = relationship(
        "TokenPosition", back_populates="rfc", cascade="all, delete-orphan"
    )


class Author(Base):
    __tablename__ = 'authors'

    rfc_num: Mapped[int] = mapped_column(
        Integer, ForeignKey('rfc.num'), primary_key=True, index=True
    )
    author_name: Mapped[str] = mapped_column(String, primary_key=True)

    rfc: Mapped["Rfc"] = relationship("Rfc", back_populates="authors")


class RfcSection(Base):
    __tablename__ = 'rfc_section'

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    rfc_num: Mapped[int] = mapped_column(
        Integer, ForeignKey('rfc.num'), index=True
    )
    index: Mapped[int] = mapped_column(Integer)
    content: Mapped[str] = mapped_column(Text)
    row_start: Mapped[int] = mapped_column(Integer)
    row_end: Mapped[int] = mapped_column(Integer)
    indentation: Mapped[int] = mapped_column(Integer)

    rfc: Mapped["Rfc"] = relationship("Rfc", back_populates="sections")
    token_positions: Mapped[list["TokenPosition"]] = relationship(
        "TokenPosition", back_populates="section"
    )


class Token(Base):
    __tablename__ = 'token'

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    token: Mapped[str] = mapped_column(String, index=True)
    stem: Mapped[str] = mapped_column(String, index=True)

    token_positions: Mapped[list["TokenPosition"]] = relationship(
        "TokenPosition", back_populates="token"
    )
    token_groups: Mapped[list["TokenToGroup"]] = relationship(
        "TokenToGroup", back_populates="token"
    )
    phrase_tokens: Mapped[list["PhraseToken"]] = relationship(
        "PhraseToken", back_populates="token"
    )


class TokenPosition(Base):
    __tablename__ = 'token_position'

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    token_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('token.id'), index=True
    )
    rfc_num: Mapped[int] = mapped_column(
        Integer, ForeignKey('rfc.num'), index=True
    )
    page: Mapped[int] = mapped_column(Integer, index=True)
    row: Mapped[int] = mapped_column(Integer, index=True)

    start_position: Mapped[int] = mapped_column(Integer)
    end_position: Mapped[int] = mapped_column(Integer)
    index: Mapped[int] = mapped_column(Integer)

    section_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('rfc_section.id'), index=True
    )

    token: Mapped["Token"] = relationship(
        "Token", back_populates="token_positions"
    )
    rfc: Mapped["Rfc"] = relationship("Rfc", back_populates="token_positions")
    section: Mapped["RfcSection"] = relationship(
        "RfcSection", back_populates="token_positions"
    )


class TokenGroup(Base):
    __tablename__ = 'token_group'

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    group_name: Mapped[str] = mapped_column(String, index=True, unique=True)

    tokens: Mapped[list["TokenToGroup"]] = relationship(
        "TokenToGroup", back_populates="group"
    )


class TokenToGroup(Base):
    __tablename__ = 'token_to_group'

    token_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('token.id'), primary_key=True
    )
    group_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('token_group.id'), primary_key=True
    )

    token: Mapped["Token"] = relationship(
        "Token", back_populates="token_groups"
    )
    group: Mapped["TokenGroup"] = relationship(
        "TokenGroup", back_populates="tokens"
    )


class Phrase(Base):
    __tablename__ = 'phrase'

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    phrase_name: Mapped[str] = mapped_column(String, unique=True)

    content: Mapped[str] = mapped_column(Text)

    tokens: Mapped[list["PhraseToken"]] = relationship(
        "PhraseToken", back_populates="phrase"
    )


class PhraseToken(Base):
    __tablename__ = 'phrase_tokens'

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    phrase_id: Mapped[int] = mapped_column(Integer, ForeignKey('phrase.id'))
    token_id: Mapped[int] = mapped_column(Integer, ForeignKey('token.id'))
    index: Mapped[int] = mapped_column(Integer)

    phrase: Mapped["Phrase"] = relationship("Phrase", back_populates="tokens")
    token: Mapped["Token"] = relationship(
        "Token", back_populates="phrase_tokens"
    )
