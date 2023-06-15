"""This module contains the process for converting the World Bank's Documents and Rerports
metadata into the format that can be used for the LLM4Data.
"""
import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple, Union
from urllib.parse import urlparse

import pandas as pd
from metaschema.doc import (
    Model,
    DocumentDescription,
    TitleStatement,
    Author,
    RefCountryItem,
    GeographicUnit,
    Language,
    Keyword,
    Topic,
    Theme,
    Discipline,
    Tag,
)
from tqdm import tqdm


WHITESPACE_RE = re.compile("\s+")
AUTHOR_RE = re.compile(r"(.*?),\s*(.*)")
TOPICV3_RE = re.compile(r"(.*?) (m\d+ \d+)(?:,|$)")


class WBDocsToSchema:
    def __init__(self, metadata) -> None:
        self.metadata = metadata
        self

    def schema(self):
        return Model(
            document_description=DocumentDescription(
                title_statement=self.title_statement(),
                authors=self.authors(),
                date_created=self.date_created(),
                date_available=self.date_available(),
                date_published=self.date_published(),
                type=self.type(),
                status=self.status(),
                abstract=self.abstract(),
                ref_country=self.ref_country(),
                geographic_units=self.geographic_units(),
                languages=self.languages(),
                volume=self.volume(),
                number=self.number(),
                series=self.series(),
                booktitle=self.booktitle(),
                url=self.url(),
                security_classification=self.security_classification(),
                keywords=self.keywords(),
                themes=self.themes(),
                topics=self.topics(),
                disciplines=self.disciplines(),
            ),
            tags=self.tags(),
        )

    def volume(self):
        return self.metadata.get("volnb", None)

    def number(self):
        return self.metadata.get("repnb", None)

    def series(self):
        return self.metadata.get("colti", None)

    def booktitle(self):
        return self.get_repnme(self.metadata)

    def url(self):
        return self.metadata.get("pdfurl", None) or self.metadata.get("url", None)

    def security_classification(self):
        return self.metadata.get("seccl", None)

    def keywords(self):
        keywords = self.get_keywords(self.metadata)

        if keywords:
            keywords = [Keyword(name=keyword) for keyword in keywords]

        return keywords

    def themes(self):
        majtheme = self.get_majtheme(self.metadata)
        theme = self.get_theme(self.metadata)

        themes = None

        if majtheme:
            themes = [Theme(name=th, vocabulary="majtheme") for th in majtheme]

        if theme:
            themes = themes or []
            themes.extend([Theme(name=th, vocabulary="theme") for th in theme])

        return themes

    def topics(self):
        topic_keys = ["historic_topic", "subtopic", "topic", "teratopic"]
        topics = []

        topicv3 = WHITESPACE_RE.sub(" ", self.metadata.get("topicv3", ""))
        if topicv3:
            for name, id in TOPICV3_RE.findall(topicv3):
                topics.append(
                    Topic(id=id.strip(), name=name.strip(), vocabulary="topicv3")
                )

        for key in topic_keys:
            topic_list = self.make_unique_entry(self.metadata.get(key, "")) or []

            for name in topic_list:
                topics.append(Topic(name=name.strip(), vocabulary=key))

        return None if len(topics) == 0 else topics

    def disciplines(self):
        disciplines = []
        subsc = self.comma_separated_list(self.metadata, "subsc")

        if subsc:
            for sub in subsc:
                disciplines.append(Discipline(name=sub, vocabulary="subsc"))

        sectr = self.numbered_list(self.metadata.get("sectr"), "sector", delimiter=None)

        if sectr:
            for sec in sectr:
                disciplines.append(Discipline(name=sec, vocabulary="sectr"))

        disciplines = disciplines or None

        return disciplines

    def tags(self):
        # projectid (PROJECT ID)
        tag_tag_group = dict(
            projectid="PROJECT ID",
            owner="WB OWNING UNIT",
            prdln="PRODUCT LINE",
            loan_no="LOAN NO",
            lndinstr="LENDING INSTRUMENT",
            envcat="ENVIRONMENTAL CATEGORY",
        )
        tags = []

        for key, tag_group in tag_tag_group.items():
            # print(key, tag_group)
            if key not in self.metadata:
                continue

            if key != "lndinstr":
                tag_list = self.get_unique_list(
                    self.comma_separated_list(self.metadata, key)
                )
            else:
                tag_list = self.numbered_list(
                    self.metadata.get(key), key, delimiter=None
                )

            for tag in tag_list:
                tags.append(Tag(tag=tag, tag_group=tag_group))

        tags = tags or None

        return tags

    def title_statement(self):
        return TitleStatement(
            idno=self.metadata["id"],
            title=self.get_title(self.metadata),
        )

    def authors(self):
        return self.get_author(self.metadata)

    def date_created(self):
        return self.metadata.get("docdt", None)

    def date_available(self):
        return self.metadata.get("disclosure_date", None)

    def date_published(self):
        return self.metadata.get("ext_pub_date", None)

    def type(self):
        majdocty = self.metadata.get("majdocty", None)
        docty = self.metadata.get("docty", None)

        value = ""

        if majdocty:
            value = majdocty

        if docty:
            value = f"{value} :: {docty}"

        return value

    def status(self):
        return self.metadata.get("disclosure_type", None)

    def abstract(self):
        return WHITESPACE_RE.sub(" ", self.get_abstract(self.metadata))

    def ref_country(self):
        countries = self.get_country(self.metadata)

        if countries:
            countries = [
                RefCountryItem(name=country, code=None) for country in countries
            ]

        return countries

    def geographic_units(self):
        regions = self.get_adm_region(self.metadata)

        if regions:
            regions = [
                GeographicUnit(
                    name=region,
                    code=None,
                    type="WB Administrative Region",
                )
                for region in regions
            ]

        return None

    def languages(self):
        lang = self.get_language(self.metadata)

        if lang:
            lang = [Language(name=lang, code=None)]

        return lang

    ##############################
    # Helper functions
    ##############################

    def get_abstract(self, metadata):
        # "abstracts": {
        #     "cdata!": "This press release announces the\n            World Bank has approved six loans totaling two hundred\n            twenty-seven million dollars to Congo, India, Sudan,\n            Tunisia, and Zaire."
        # },

        abstract = ""
        if "abstracts" in metadata and isinstance(metadata["abstracts"], dict):
            abstract = metadata["abstracts"].get("cdata!")

        return abstract

    def get_repnme(self, metadata):
        # "repnme": {
        #     "repnme": "Wage differentials between the public and\n            private sector in India"
        # },

        repnme = ""
        if "repnme" in metadata and isinstance(metadata["repnme"], dict):
            repnme = metadata["repnme"].get("repnme")
            repnme = WHITESPACE_RE.sub(" ", repnme)

        return repnme

    def get_majtheme(self, metadata, delimiter=";"):
        # "majtheme": "Financial and private sector development,Public sector governance",
        # return self.get_unique_list(metadata.get("majtheme", "").split(","))
        return self.comma_separated_list(metadata, "majtheme", delimiter)

    def get_theme(self, metadata, delimiter=";"):
        # "theme": "Public sector governance,Financial and private sector development",
        return self.comma_separated_list(metadata, "theme", delimiter)

    def get_country(self, metadata, delimiter=";"):
        # "count": "Congo, Republic of,India,Sudan,Tunisia,Congo, Democratic Republic of",
        return self.comma_separated_list(metadata, "count", delimiter)

    def comma_separated_list(self, metadata, key, delimiter=";"):
        p = re.compile("(\S),(\S)")
        values = p.sub(f"\\1{delimiter}\\2", metadata.get(key, "")).strip()
        values = values.split(delimiter) if values else []

        return values

    def get_adm_region(self, metadata):
        # "admreg": "Africa,Africa,East Asia and Pacific,East Asia and Pacific,Europe and Central Asia,Europe and Central Asia",
        return self.make_unique_entry(metadata.get("admreg", ""))

    def get_title(self, metadata):
        # "display_title": [
        #     {
        #     "display_title": "Issues and options in the design\n            of GEF-supported trust funds for biodiversity conservation"
        #     }
        # ],
        dspt = metadata.get("display_title", None)
        if dspt:
            if isinstance(dspt, str):
                dspt = dspt
            elif isinstance(dspt, list):
                dspt = dspt[0].get("display_title")
            else:
                raise ValueError(f"display_title format unknown: {dspt}")

            if isinstance(dspt, str):
                dspt = WHITESPACE_RE.sub(" ", dspt)
                dspt = dspt.strip()

        return dspt

    def get_author(self, metadata, delimiter=";"):
        # "authors": {
        #     "0": {
        #       "author": "Sjoberg,Fredrik Matias"
        #     },
        #     "1": {
        #       "author": "Mellon,Jonathan"
        #     },
        #     "2": {
        #       "author": "Peixoto,Tiago Carneiro"
        #     },
        #     "3": {
        #       "author": "Hemker,Johannes Zacharias"
        #     },
        #     "4": {
        #       "author": "Tsai,Lily Lee"
        #     }
        # },

        authors = metadata.get("authors")

        authors_value = None
        if authors and isinstance(authors, dict):
            authors_value = self.get_unique_list(
                [author["author"] for author in authors.values()]
            )
            authors_value = delimiter.join(authors_value)

        authors = authors_value

        # authors = "Runji,Justin;Jose Rizal;Bonifacio, Andres; Damaso, Maria Clara"
        if not isinstance(authors, str):
            return None

        authors_list = []

        for author in authors.split(delimiter):
            author = author.strip()
            first_name = None
            last_name = None
            full_name = None

            match = AUTHOR_RE.match(author)
            if match:
                first_name = match.group(2)
                last_name = match.group(1)
            else:
                full_name = author.strip()

            authors_list.append(
                Author(
                    first_name=first_name,
                    last_name=last_name,
                    full_name=full_name,
                )
            )

        return authors_list

    def numbered_list(self, values, key, delimiter=";"):
        if values and isinstance(values, dict):
            values = self.get_unique_list(
                [value.get(key) for value in values.values() if value.get(key)]
            )
            if delimiter:
                values = delimiter.join(values)

        return values

    def get_keywords(self, metadata):
        # "keywd": {
        #     "0": {
        #       "keywd": "plastic waste; catchment; waste handling\n            practices; terrestrial environment; illegal dumping;\n            frequency of rainfall events"
        #     }
        # }
        keywds = metadata.get("keywd")

        keywords = None
        if keywds and isinstance(keywds, dict):
            keywds = [
                kwd.strip()
                for keywd in keywds.values()
                for kwd in WHITESPACE_RE.sub(" ", keywd["keywd"]).split(";")
            ]
            keywords = self.get_unique_list(keywds)

        return keywords

    def get_language(self, metadata):
        # "lang": "English",
        return metadata.get("lang")

    def get_unique_list(self, values):
        unique_list = sorted(set([i.strip() for i in values if i.strip()]))

        if not unique_list or unique_list == [""]:
            unique_list = None

        return unique_list

    def normalize_set(self, s):
        # s = set(['Publications & Research', 'Publications'])

        l = sorted(s)
        remove_index = set()

        for i in range(len(l) - 1):
            for j in range(1, len(l)):
                if l[i] in l[j]:
                    remove_index.add(i)

        for k in sorted(remove_index, reverse=True):
            l.pop(k)

        return l

    def make_unique_entry(self, entries):
        # This will remove duplicate entries in fields: `majdocty` (`majdoctype` : normalized) and `admreg`
        entries = entries.strip()

        if entries:
            entries = self.normalize_set(
                set([i.strip() for i in entries.split(",") if i.strip()])
            )
            if len(entries) == 0:
                entries = None
        else:
            entries = None

        return entries


# class WBDocsNormalizer:
#     def __init__(self, metadata):
#         self.metadata = metadata

#     def normalize(self):
#         metadata = self.metadata
#         item = {}

#         item["abstract"] = self.get_abstract(metadata)
#         item["adm_region"] = self.get_adm_region(metadata)
#         item["author"] = self.get_author(metadata)

#         item["collection"] = self.get_collection(metadata)
#         item["corpus"] = "WB"
#         item["country"] = self.get_country(metadata)

#         item["date_published"] = self.get_date_published(metadata)
#         item["digital_identifier"] = self.get_digital_identifier(metadata)
#         item["doc_type"] = self.get_doc_type(metadata)

#         item["geo_region"] = self.get_geo_region(metadata)

#         item["keywords"] = self.get_keywords(metadata)

#         item["language_src"] = self.get_language_src(metadata)

#         item["major_doc_type"] = self.get_major_doc_type(metadata)

#         item["project_id"] = self.get_wb_project_id(metadata)

#         item["title"] = self.get_title(metadata)
#         item["topics_src"] = self.get_topics_src(metadata)

#         item["url_pdf"] = metadata.get("pdfurl")
#         item["url_source"] = metadata.get("url_friendly_title", metadata.get("url"))
#         item["url_txt"] = metadata.get("txturl")

#         item["year"] = item["date_published"].split(
#             "-")[0] if (item["date_published"] and "-" in item["date_published"]) else None

#         item["src_metadata"] = metadata

#         return item

#     def normalize_set(self, s):
#         # s = set(['Publications & Research', 'Publications'])

#         l = sorted(s)
#         remove_index = set()

#         for i in range(len(l) - 1):
#             for j in range(1, len(l)):
#                 if l[i] in l[j]:
#                     remove_index.add(i)

#         for k in sorted(remove_index, reverse=True):
#             l.pop(k)

#         return l

#     def make_unique_entry(self, entries):
#         # This will remove duplicate entries in fields: `majdocty` (`majdoctype` : normalized) and `admreg`
#         entries = entries.strip()
#         if entries:
#             entries = self.normalize_set(
#                 set([i.strip() for i in entries.split(',') if i.strip()]))
#             if len(entries) == 0:
#                 entries = None
#         else:
#             entries = None

#         return entries

#     def get_abstract(self, metadata):
#         # "abstracts": {
#         #     "cdata!": "This press release announces the\n            World Bank has approved six loans totaling two hundred\n            twenty-seven million dollars to Congo, India, Sudan,\n            Tunisia, and Zaire."
#         # },

#         abstract = ""
#         if "abstracts" in metadata and isinstance(metadata["abstracts"], dict):
#             abstract = metadata["abstracts"].get("cdata!")
#         return abstract

#     def get_adm_region(self, metadata):
#         # "admreg": "Africa,Africa,East Asia and Pacific,East Asia and Pacific,Europe and Central Asia,Europe and Central Asia",
#         return self.make_unique_entry(metadata.get('admreg', ''))

#     def get_author(self, metadata, delimiter=";"):
#         # "authors": {
#         #     "0": {
#         #       "author": "Sjoberg,Fredrik Matias"
#         #     },
#         #     "1": {
#         #       "author": "Mellon,Jonathan"
#         #     },
#         #     "2": {
#         #       "author": "Peixoto,Tiago Carneiro"
#         #     },
#         #     "3": {
#         #       "author": "Hemker,Johannes Zacharias"
#         #     },
#         #     "4": {
#         #       "author": "Tsai,Lily Lee"
#         #     }
#         # },

#         authors = metadata.get("authors")

#         authors_value = None
#         if authors and isinstance(authors, dict):
#             authors_value = self.get_unique_list(
#                 [author["author"] for author in authors.values()])
#             authors_value = delimiter.join(authors_value)

#         return self.standardize_authors_list(authors_value, delimiter=delimiter)

#     def standardize_authors_list(self, authors, delimiter=";"):
#         # authors = "Runji,Justin;Jose Rizal;Bonifacio, Andres; Damaso, Maria Clara"
#         if not isinstance(authors, str):
#             return []
#         return [re.sub(r"(.*),\s*(.*)", r"\2 \1", i.strip()) for i in authors.split(delimiter)]

#     def get_collection(self, metadata):
#         return metadata.get("colti")

#     def get_country(self, metadata, delimiter=";"):
#         # "count": "Congo, Republic of,India,Sudan,Tunisia,Congo, Democratic Republic of",
#         p = re.compile("(\S),(\S)")
#         country = p.sub(f"\\1{delimiter}\\2", metadata.get("count", ""))
#         country = country.split(delimiter)
#         country = country if country else None

#         return country

#     def get_date_published(self, metadata):
#         # "docdt": "1981-09-30T00:00:00Z",
#         date = metadata.get("docdt", "T").split("T")[0]
#         if not date:
#             date = None
#         return date

#     def get_digital_identifier(self, metadata):
#         # "docm_id": "090224b086412c6c",
#         return metadata.get("docm_id", "")

#     def get_doc_type(self, metadata):
#         # "docty": "Agenda",
#         return self.make_unique_entry(metadata.get('docty', ''))

#     def get_geo_region(self, metadata):
#         # "geo_regions": {
#         #     "0": {
#         #       "geo_region": "South Eastern Europe and Balkans"
#         #     },
#         #     "1": {
#         #       "geo_region": "South Eastern Europe and Balkans"
#         #     },
#         # },

#         geo_regions = metadata.get("geo_regions")

#         geo_region = None
#         if geo_regions and isinstance(geo_regions, dict):
#             geo_region = self.get_unique_list(
#                 [geo_region["geo_region"] for geo_region in geo_regions.values()])

#         return geo_region

#     def get_keywords(self, metadata):
#         # "keywd": {
#         #     "0": {
#         #       "keywd": "plastic waste; catchment; waste handling\n            practices; terrestrial environment; illegal dumping;\n            frequency of rainfall events"
#         #     }
#         # }
#         keywds = metadata.get("keywd")

#         keywords = None
#         if keywds and isinstance(keywds, dict):
#             keywds = [kwd.strip() for keywd in keywds.values()
#                       for kwd in WHITESPACE_RE.sub(" ", keywd["keywd"]).split(";")]
#             keywords = self.get_unique_list(keywds)

#         return keywords

#     def get_language_src(self, metadata):
#         # "lang": "English",
#         return metadata.get("lang")

#     def get_major_doc_type(self, metadata):
#         # "majdocty": "Publications & Research",
#         return self.make_unique_entry(metadata.get('majdocty', ''))

#     def get_pdf_link(self, metadata):
#         pdfurl = metadata.get("pdfurl")

#         if not pdfurl:
#             # Attempt to recover pdfurl from txturl.
#             pdfurl = metadata.get("txturl")

#             if pdfurl:
#                 pdfurl = pdfurl.replace("/text/", "/pdf/")
#                 pdfurl = f"{os.path.splitext(pdfurl)[0]}.pdf"

#         return pdfurl

#     def get_title(self, metadata):
#         # "display_title": [
#         #     {
#         #     "display_title": "Issues and options in the design\n            of GEF-supported trust funds for biodiversity conservation"
#         #     }
#         # ],
#         dspt = metadata.get("display_title", None)
#         if dspt:
#             if isinstance(dspt, str):
#                 dspt = dspt
#             elif isinstance(dspt, list):
#                 dspt = dspt[0].get("display_title")
#             else:
#                 raise ValueError(f"display_title format unknown: {dspt}")
#         return dspt

#     def get_topics_src(self, metadata):
#         # "historic_topic": "Education,Environment,Energy,Rural Development,Water Resources",
#         return metadata.get("historic_topic", "").split(",")

#     def get_wb_lending_instrument(self, metadata):
#         # "lndinstr": {
#         #     "0": {
#         #       "lndinstr": "Technical Assistance Loan"
#         #     },
#         #     "1": {
#         #       "lndinstr": "Technical Assistance Loan"
#         #     },
#         #     "2": {
#         #       "lndinstr": "Technical Assistance Loan"
#         #     }
#         # },

#         lndinstrs = metadata.get("lndinstr")

#         lending_instrument = None
#         if lndinstrs and isinstance(lndinstrs, dict):
#             lending_instrument = self.get_unique_list(
#                 [lndinstr["lndinstr"] for lndinstr in lndinstrs.values()])

#         return lending_instrument

#     def get_wb_major_theme(self, metadata):
#         # "majtheme": "Financial and private sector development,Public sector governance",
#         return self.get_unique_list(metadata.get("majtheme", "").split(","))

#     def get_wb_product_line(self, metadata):
#         # "prdln": "IBRD/IDA",
#         return metadata.get("prdln")

#     def get_wb_project_id(self, metadata):
#         # "projectid": "P003677,P008088,P000544,P004440",
#         return self.get_unique_list(metadata.get("projectid", "").split(","))

#     def get_wb_sector(self, metadata):
#         # "sectr": {
#         #     "0": {
#         #       "sector": "Transportation"
#         #     },
#         #     "1": {
#         #       "sector": "Agriculture, Fishing and Forestry"
#         #     }
#         # },
#         sectr = metadata.get("sectr")

#         sectors = None
#         if sectr and isinstance(sectr, dict):
#             sectors = self.get_unique_list(
#                 [sector["sector"] for sector in sectr.values()])

#         return sectors

#     def get_wb_subtopic_src(self, metadata):
#         # "subtopic": "Public Sector Economics,Municipal Financial Management,Strategic Debt Management,Banks & Banking Reform,External Debt",
#         return self.get_unique_list(metadata.get("subtopic", "").split(","))

#     def get_wb_theme(self, metadata):
#         # "theme": "State-owned enterprise restructuring and privatization,Other financial and private sector development,International financial standards and systems,Other public sector governance",
#         return self.get_unique_list(metadata.get("theme", "").split(","))

#     def get_unique_list(self, values):
#         unique_list = sorted(set([i.strip() for i in values if i.strip()]))

#         if not unique_list or unique_list == [""]:
#             unique_list = None

#         return unique_list
