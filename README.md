![](https://img.shields.io/badge/Built%20with%20%E2%9D%A4%EF%B8%8F-at%20Technologiestiftung%20Berlin-blue)

<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->

[![All Contributors](https://img.shields.io/badge/all_contributors-0-orange.svg?style=flat-square)](#contributors-)

<!-- ALL-CONTRIBUTORS-BADGE:END -->

# GeoExplorer Data

This repository includes the data logic behind [GeoExplorer](https://github.com/technologiestiftung/odis-geoexplorer) — an AI-driven search interface for Berlin's geospatial datasets.

The [Jupyter Notebook](index.ipynb) contains scripts to:

- **Scrape** metadata from Berlin’s CSW geodata catalog
- **Embed** metadata using OpenAI’s embeddings and store it in Supabase
- **Analyze** and visualize the data in a 2D scatterplot view for the GeoExplorer UI

---

## Setup

### 1. Database Setup

You can set up a Supabase database using Docker (for local development) or via [Supabase.io](https://supabase.io).

Create the necessary table and function using the SQL below:

```sql
-- Create the table
create table if not exists nods_page_section_v2 (
  id uuid primary key,
  slug text,
  heading text,
  dataset_info jsonb,
  embedding vector(1536) -- 1536 for text-embedding-3-small
);

-- create the function
-- create the function
create or replace function match_page_sections_v2(
  query_embedding vector(1536),
  match_threshold float,
  match_count int
)
returns table (
  id uuid,
  slug text,
  heading text,
  similarity float,
  dataset_info jsonb
)
language plpgsql
as $$
begin
  return query
  select
    s.id,
    s.slug,
    s.heading,
    (s.embedding <#> query_embedding) * -1 as similarity,
    s.dataset*info
  from nods_page_section_v2 s
  -- The dot product is negative because of a Postgres limitation, so we negate it
  where (nods_page_section_v2.embedding <#> embedding) * -1 > match_threshold
  order by nods_page_section_v2.embedding <#> embedding
  limit match_count;
end;
$$;

```

### 2. Environment Setup

Duplicate the `.env.example` file and rename it to `.env`. Then provide either your local connection details or those from Supabase, depending on where you want to save your data.

- To retrieve your local `NEXT_PUBLIC_SUPABASE_ANON_KEY` and `SUPABASE_SERVICE_ROLE_KEY` run:

```bash
npx supabase status
```

You will also need to provide a key to use **OpenAI API**.

### 3. Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

### 4. Run the Notebook

Open and execute `index.ipynb` to run the pipeline.

## ToDos

- Script for removing deleted datasets

## Contributing

Before you create a pull request, write an issue so we can discuss your changes.

## Contributors

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://hanshack.com/"><img src="https://avatars.githubusercontent.com/u/8025164?v=4?s=64" width="64px;" alt="Hans Hack"/><br /><sub><b>Hans Hack</b></sub></a><br /><a href="https://github.com/technologiestiftung/odis-geoexplorer/commits?author=hanshack" title="Code">💻</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!

## Content Licensing

Texts and content available as [CC BY](https://creativecommons.org/licenses/by/3.0/de/).

## Credits

<table>
  <tr>
      <td>
      Made by: <a href="https://odis-berlin.de">
        <br />
        <br />
        <img width="200" src="https://logos.citylab-berlin.org/logo-odis-berlin.svg" />
      </a>
    </td>
    <td>
       Together with: <a href="https://citylab-berlin.org/de/start/">
        <br />
        <br />
        <img width="200" src="https://logos.citylab-berlin.org/logo-citylab-berlin.svg" />
      </a>
    </td>
    <td>
      A project by <a href="https://www.technologiestiftung-berlin.de/">
        <br />
        <br />
        <img width="150" src="https://logos.citylab-berlin.org/logo-technologiestiftung-berlin-de.svg" />
      </a>
    </td>
    <td>
      Supported by <a href="https://www.berlin.de/rbmskzl/">
        <br />
        <br />
        <img width="80" src="https://logos.citylab-berlin.org/logo-berlin-senatskanzelei-de.svg" />
      </a>
    </td>
  </tr>
</table>

## Related Projects

[GeoExplorer](https://github.com/technologiestiftung/odis-geoexplorer/)

[WFS-Explorer](https://github.com/technologiestiftung/odis-wfsexplorer/)
