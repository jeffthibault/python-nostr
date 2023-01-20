from collections import UserList
from typing import List

from .event import Event, EventKind



class Filter:
    """
    NIP-01 filtering.

    Explicitly supports "#e" and "#p" tag filters via `event_refs` and `pubkey_refs`.

    Arbitrary NIP-12 single-letter tag filters are also supported via `add_arbitrary_tag`.
    If a particular single-letter tag gains prominence, explicit support should be
    added. For example:
        # arbitrary tag
        filter.add_arbitrary_tag('t', [hashtags])
    
        # promoted to explicit support
        Filter(hashtag_refs=[hashtags])
    """
    def __init__(
            self, 
            event_ids: List[str] = None, 
            kinds: List[EventKind] = None, 
            authors: List[str] = None, 
            since: int = None, 
            until: int = None, 
            event_refs: List[str] = None,       # the "#e" attr; list of event ids referenced in an "e" tag
            pubkey_refs: List[str] = None,      # The "#p" attr; list of pubkeys referenced in a "p" tag
            limit: int = None) -> None:
        self.event_ids = event_ids
        self.kinds = kinds
        self.authors = authors
        self.since = since
        self.until = until
        self.event_refs = event_refs
        self.pubkey_refs = pubkey_refs
        self.limit = limit

        self.tags = {}
        if self.event_refs:
            self.tags["#e"] = self.event_refs
        if self.pubkey_refs:
            self.tags["#p"] = self.pubkey_refs


    def add_arbitrary_tag(self, tag_letter: str, values: list):
        """ NIP-12: Filter on any arbitrary single-letter tag """
        if len(tag_letter) != 1 or not tag_letter.isalpha:
            raise Exception("NIP-12 only supports single-letter arbitrary tags")
        
        self.tags[f"#{tag_letter}"] = values


    def matches(self, event: Event) -> bool:
        if self.event_ids is not None and event.id not in self.event_ids:
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

        if self.tags:
            for target_tag, target_values in self.tags.items():
                target_tag = target_tag[1]  # Just use the single-letter; omit the "#"
                print(f"target_tag: {target_tag}")
                if target_tag not in [tag[0] for tag in event.tags]:
                    # Event doesn't have one of our filter target tags
                    return False

                # Event does have the target tag, but does it match all target values
                for tag_list in event.tags:
                    # ['x', "val1", "val2", "val3", ...]
                    print(f"tag_list: {tag_list}")
                    if tag_list[0] == target_tag:
                        for target_val in target_values:
                            if target_val not in tag_list[1:]:
                                return False

        return True


    def to_json_object(self) -> dict:
        res = {}
        if self.ids is not None:
            res["ids"] = self.event_ids
        if self.kinds is not None:   
            res["kinds"] = self.kinds
        if self.authors is not None:
            res["authors"] = self.authors
        if self.since is not None:
            res["since"] = self.since
        if self.until is not None:
            res["until"] = self.until
        if self.limit is not None:
            res["limit"] = self.limit
        if self.tags:
            res.update(self.tags)

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