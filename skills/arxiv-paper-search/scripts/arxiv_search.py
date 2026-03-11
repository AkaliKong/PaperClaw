#!/usr/bin/env python3
"""
arXiv 论文通用搜索工具
支持关键词、主题、作者查询，可设置时间范围

使用 arXiv HTTP API（无需 arxiv 包），纯标准库实现。
"""

import argparse
import os
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from typing import List, Optional


# XML namespace used by arXiv Atom feed
NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "arxiv": "http://arxiv.org/schemas/atom",
    "opensearch": "http://a9.com/-/spec/opensearch/1.1/",
}

ARXIV_API = "https://export.arxiv.org/api/query"


class ArxivSearcher:
    """arXiv 论文搜索器（纯 HTTP + 标准库实现，无需 arxiv 包）"""

    CATEGORIES = {
        "ai": "cs.AI",
        "ml": "cs.LG",
        "nlp": "cs.CL",
        "cv": "cs.CV",
        "ir": "cs.IR",
        "se": "cs.SE",
        "db": "cs.DB",
        "net": "cs.NI",
        "crypto": "cs.CR",
        "robotics": "cs.RO",
        "stat": "stat.ML",
    }

    def __init__(self, download_dir: str = None):
        self.download_dir = download_dir or os.path.expanduser("~/Downloads/arxiv_papers")

    # ------------------------------------------------------------------ #
    # Query builder                                                        #
    # ------------------------------------------------------------------ #

    def build_query(
        self,
        keywords: Optional[List[str]] = None,
        title: Optional[str] = None,
        author: Optional[str] = None,
        abstract: Optional[str] = None,
        categories: Optional[List[str]] = None,
        arxiv_id: Optional[str] = None,
        keyword_mode: str = "or",
    ) -> str:
        if arxiv_id:
            return arxiv_id

        parts = []

        if keywords:
            kw_parts = []
            for kw in keywords:
                kw_parts.append(f'all:"{kw}"' if " " in kw else f"all:{kw}")
            joiner = " OR " if keyword_mode.lower() == "or" else " AND "
            parts.append(f"({joiner.join(kw_parts)})")

        if title:
            parts.append(f'ti:"{title}"' if " " in title else f"ti:{title}")

        if author:
            authors = [a.strip() for a in author.split(",")]
            au_parts = [f'au:"{a}"' if " " in a else f"au:{a}" for a in authors]
            parts.append(f"({' OR '.join(au_parts)})")

        if abstract:
            parts.append(f'abs:"{abstract}"' if " " in abstract else f"abs:{abstract}")

        if categories:
            resolved = []
            for cat in categories:
                cat = cat.strip().lower()
                resolved.append(self.CATEGORIES.get(cat, cat))
            cat_parts = [f"cat:{c}" for c in resolved]
            parts.append(f"({' OR '.join(cat_parts)})")

        return " AND ".join(parts) if parts else "all:*"

    # ------------------------------------------------------------------ #
    # Search                                                               #
    # ------------------------------------------------------------------ #

    def search(
        self,
        keywords: Optional[List[str]] = None,
        title: Optional[str] = None,
        author: Optional[str] = None,
        abstract: Optional[str] = None,
        categories: Optional[List[str]] = None,
        arxiv_id: Optional[str] = None,
        days: int = 365,
        max_results: int = 50,
        sort_by: str = "submitted",
        keyword_mode: str = "or",
    ) -> List[dict]:
        query = self.build_query(
            keywords=keywords,
            title=title,
            author=author,
            abstract=abstract,
            categories=categories,
            arxiv_id=arxiv_id,
            keyword_mode=keyword_mode,
        )

        sort_map = {
            "submitted": "submittedDate",
            "relevance": "relevance",
            "updated": "lastUpdatedDate",
        }
        sort_by_api = sort_map.get(sort_by, "submittedDate")

        print(f"查询语句: {query}")
        print(f"时间范围: 最近 {days} 天")
        print("-" * 60)

        cutoff_date = datetime.now(tz=timezone.utc) - timedelta(days=days)

        results = []
        batch = min(max_results * 2, 100)  # fetch larger batch for time filtering
        start = 0
        fetched = 0

        while len(results) < max_results:
            params = urllib.parse.urlencode({
                "search_query": query,
                "start": start,
                "max_results": batch,
                "sortBy": sort_by_api,
                "sortOrder": "descending",
            })
            url = f"{ARXIV_API}?{params}"

            for attempt in range(3):
                try:
                    with urllib.request.urlopen(url, timeout=30) as resp:
                        xml_data = resp.read()
                    break
                except Exception as exc:
                    if attempt == 2:
                        raise
                    time.sleep(3 * (attempt + 1))

            root = ET.fromstring(xml_data)

            entries = root.findall("atom:entry", NS)
            if not entries:
                break

            for entry in entries:
                fetched += 1

                # --- published date ---
                pub_str = _text(entry, "atom:published", NS)
                try:
                    pub_dt = datetime.fromisoformat(pub_str.rstrip("Z")).replace(tzinfo=timezone.utc)
                except Exception:
                    continue

                if pub_dt < cutoff_date:
                    continue

                # --- updated date ---
                upd_str = _text(entry, "atom:updated", NS)
                try:
                    upd_dt = datetime.fromisoformat(upd_str.rstrip("Z")).replace(tzinfo=timezone.utc)
                except Exception:
                    upd_dt = pub_dt

                # --- id ---
                raw_id = _text(entry, "atom:id", NS) or ""
                arxiv_abs_id = raw_id.split("/abs/")[-1] if "/abs/" in raw_id else raw_id.split("/")[-1]

                # --- title / summary ---
                title_txt = (_text(entry, "atom:title", NS) or "").replace("\n", " ").strip()
                summary_txt = (_text(entry, "atom:summary", NS) or "").replace("\n", " ").strip()

                # --- authors ---
                authors = []
                for author_el in entry.findall("atom:author", NS):
                    name_el = author_el.find("atom:name", NS)
                    if name_el is not None and name_el.text:
                        authors.append(name_el.text.strip())

                # --- categories ---
                primary_cat_el = entry.find("arxiv:primary_category", NS)
                primary_cat = primary_cat_el.attrib.get("term", "") if primary_cat_el is not None else ""
                all_cats = [c.attrib.get("term", "") for c in entry.findall("atom:category", NS)]
                if primary_cat and primary_cat not in all_cats:
                    all_cats.insert(0, primary_cat)

                # --- links ---
                pdf_url = ""
                arxiv_url = raw_id
                for link_el in entry.findall("atom:link", NS):
                    if link_el.attrib.get("type") == "application/pdf":
                        pdf_url = link_el.attrib.get("href", "")
                    if link_el.attrib.get("rel") == "alternate":
                        arxiv_url = link_el.attrib.get("href", raw_id)

                # --- comments ---
                comments_el = entry.find("arxiv:comment", NS)
                comments = (comments_el.text or "").replace("\n", " ").strip() if comments_el is not None else ""

                results.append({
                    "id": arxiv_abs_id,
                    "title": title_txt,
                    "authors": authors,
                    "summary": summary_txt,
                    "published": pub_dt.strftime("%Y-%m-%d"),
                    "updated": upd_dt.strftime("%Y-%m-%d"),
                    "categories": all_cats,
                    "pdf_url": pdf_url,
                    "arxiv_url": arxiv_url,
                    "comments": comments,
                    "affiliation": "",
                })

                if len(results) >= max_results:
                    break

            # If we got fewer entries than expected, no more pages
            if len(entries) < batch:
                break

            start += batch
            time.sleep(3)  # arXiv rate limit

        return results

    # ------------------------------------------------------------------ #
    # Display                                                              #
    # ------------------------------------------------------------------ #

    def display(self, results: List[dict], verbose: bool = False):
        if not results:
            print("\n未找到符合条件的论文")
            return

        print(f"\n{'='*80}")
        print(f"共找到 {len(results)} 篇论文")
        print(f"{'='*80}\n")

        for i, paper in enumerate(results, 1):
            print(f"[{i}] {paper['title']}")
            authors = ", ".join(paper["authors"][:4])
            if len(paper["authors"]) > 4:
                authors += " et al."
            print(f"    作者: {authors}")
            cats = ", ".join(paper["categories"][:3])
            print(f"    发布: {paper['published']} | 分类: {cats}")
            print(f"    链接: {paper['arxiv_url']}")
            print(f"    PDF: {paper['pdf_url']}")
            if paper.get("comments"):
                print(f"    备注: {paper['comments']}")
            if verbose:
                abstract = paper["summary"][:400] + "..." if len(paper["summary"]) > 400 else paper["summary"]
                print(f"    摘要: {abstract}")
            print()

    # ------------------------------------------------------------------ #
    # Export                                                               #
    # ------------------------------------------------------------------ #

    def export_markdown(self, results: List[dict], output_file: str = None):
        if not output_file:
            os.makedirs(self.download_dir, exist_ok=True)
            output_file = os.path.join(
                self.download_dir,
                f"search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            )

        os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)

        lines = [
            "# arXiv 论文搜索结果",
            f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**论文数量**: {len(results)} 篇",
            "",
            "---",
            "",
        ]

        for i, paper in enumerate(results, 1):
            authors = ", ".join(paper["authors"][:4])
            if len(paper["authors"]) > 4:
                authors += " et al."
            entry = [
                f"## {i}. {paper['title']}",
                "",
                f"- **作者**: {authors}",
                f"- **发布日期**: {paper['published']}",
                f"- **分类**: {', '.join(paper['categories'][:3])}",
                f"- **arXiv**: [{paper['id']}]({paper['arxiv_url']})",
                f"- **PDF**: [下载]({paper['pdf_url']})",
            ]
            if paper.get("comments"):
                entry.append(f"- **备注**: {paper['comments']}")
            entry.extend([
                "",
                f"**摘要**: {paper['summary'][:500]}{'...' if len(paper['summary']) > 500 else ''}",
                "",
                "---",
                "",
            ])
            lines.extend(entry)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        print(f"已导出: {output_file}")
        return output_file


# ------------------------------------------------------------------ #
# Helpers                                                              #
# ------------------------------------------------------------------ #


def _text(element, tag: str, ns: dict) -> str:
    """Safely get text from an XML element."""
    el = element.find(tag, ns)
    return (el.text or "").strip() if el is not None else ""


# ------------------------------------------------------------------ #
# CLI                                                                  #
# ------------------------------------------------------------------ #


def main():
    parser = argparse.ArgumentParser(
        description="arXiv 论文搜索工具（纯 HTTP，无需额外依赖）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("-k", "--keywords", nargs="+", help="关键词")
    parser.add_argument("-t", "--title", help="标题关键词")
    parser.add_argument("-a", "--author", help="作者名（多作者逗号分隔）")
    parser.add_argument("-b", "--abstract", help="摘要关键词")
    parser.add_argument("-c", "--categories", nargs="+", help="分类（如 cs.AI 或简写 ai）")
    parser.add_argument("-i", "--id", help="arXiv ID")

    parser.add_argument("--days", type=int, default=365, help="时间范围（天，默认365）")
    parser.add_argument("-n", "--num", type=int, default=20, help="返回数量（默认20）")
    parser.add_argument("-s", "--sort", choices=["submitted", "relevance", "updated"],
                        default="submitted", help="排序方式")
    parser.add_argument("--keyword-mode", choices=["or", "and"], default="or")

    parser.add_argument("-v", "--verbose", action="store_true", help="显示详细摘要")
    parser.add_argument("--export", action="store_true", help="导出为 Markdown")
    parser.add_argument("--export-file", help="导出文件路径")
    parser.add_argument("--export-dir", help="导出目录")
    parser.add_argument("--download-dir", help="PDF 下载目录")

    args = parser.parse_args()

    if not any([args.keywords, args.title, args.author, args.abstract, args.categories, args.id]):
        parser.print_help()
        print("\n错误: 请至少提供一个搜索条件")
        return

    searcher = ArxivSearcher(download_dir=args.download_dir)
    results = searcher.search(
        keywords=args.keywords,
        title=args.title,
        author=args.author,
        abstract=args.abstract,
        categories=args.categories,
        arxiv_id=args.id,
        days=args.days,
        max_results=args.num,
        sort_by=args.sort,
        keyword_mode=args.keyword_mode,
    )
    searcher.display(results, verbose=args.verbose)

    if args.export and results:
        export_file = args.export_file
        if not export_file and args.export_dir:
            export_file = os.path.join(
                args.export_dir,
                f"search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            )
        searcher.export_markdown(results, output_file=export_file)


if __name__ == "__main__":
    main()
