from collections import UserList
from typing import List

from .event import Event



class Filter:
    def __init__(
            self, 
            ids: "list[str]" = None, 
            kinds: "list[int]" = None, 
            authors: "list[str]" = None, 
            since: int = None, 
            until: int = None, 
            event_refs: List[str] = None,       # the "#e" attr; list of event ids referenced in an "e" tag
            pubkey_refs: List[str] = None,      # The "#p" attr; list of pubkeys referenced in a "p" tag
            limit: int = None) -> None:
        self.ids = ids
        self.kinds = kinds
        self.authors = authors
        self.since = since
        self.until = until
        self.event_refs = event_refs
        self.pubkey_refs = pubkey_refs
        self.limit = limit


    def matches(self, event: Event) -> bool:
        if self.ids is not None and event.id not in self.ids:
            print(f"{event.id} not in {self.ids}")
            return False
        if self.kinds is not None and event.kind not in self.kinds:
            return False
        if self.authors is not None and event.public_key not in self.authors:
            return False
        if self.since is not None and event.created_at < self.since:
            return False
        if self.until is not None and event.created_at > self.until:
            return False
        if (self.event_refs is not None or self.pubkey_refs is not None) and len(event.tags) == 0:
            return False
        if self.event_refs is not None:
            # Extract just the 'e' tag values
            event_id_refs = [tag[1] for tag in event.tags if tag[0] == "e"]
            if not event_id_refs:
                return False
            # Each event_id in the filter must be found in the Event's "e" list
            for event_id in self.event_refs:
                if event_id not in event_id_refs:
                    return False
        if self.pubkey_refs is not None:
            # Extract just the 'p' tag values
            event_pubkey_refs = [tag[1] for tag in event.tags if tag[0] == "p"]
            if not event_pubkey_refs:
                return False
            # Each pubkey in the filter must be found in the Event's "p" list
            for pubkey in self.pubkey_refs:
                if pubkey not in event_pubkey_refs:
                    return False
        return True


    def to_json_object(self) -> dict:
        res = {}
        if self.ids is not None:
            res["ids"] = self.ids
        if self.kinds is not None:   
            res["kinds"] = self.kinds
        if self.authors is not None:
            res["authors"] = self.authors
        if self.since is not None:
            res["since"] = self.since
        if self.until is not None:
            res["until"] = self.until
        if self.event_refs is not None:
            res["#e"] = self.event_refs
        if self.pubkey_refs is not None:
            res["#p"] = self.pubkey_refs
        if self.limit is not None:
            res["limit"] = self.limit

        return res



class Filters(UserList):
    def __init__(self, initlist: "list[Filter]"=[]) -> None:
        super().__init__(initlist)
        self.data: "list[Filter]"

    def match(self, event: Event):
        for filter in self.data:
            if filter.matches(event):
                return True
        return False

    def to_json_array(self) -> list:
        return [filter.to_json_object() for filter in self.data]