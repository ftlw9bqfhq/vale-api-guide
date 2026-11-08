# List charges

Returns a paginated list of charges for the account. Charges are returned newest first.

## Request

`GET /v1/charges`

### Query parameters

- `limit` - Number of objects to return, between 1 and 100. Defaults to 10.
- `starting_after` - ID of the last charge on the previous page.
- `customer` - Only return charges for this customer ID.

## Example

```
curl https://api.example.com/v1/charges \
  -H "Authorization: Bearer $KEY"
```

## Response

A charge object is returned for each entry. The `amount` will be returned in the smallest currency unit.

In order to page through results, pass the `starting_after` parameter with the ID of the last charge on the previous page. Users can also filter by `customer`, e.g. to fetch the charges of a single customer; i.e. the filter is exact.
