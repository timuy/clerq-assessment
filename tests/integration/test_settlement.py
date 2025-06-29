

from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from src.app import app

class TestSettlementEndpoint:
    """Testing Settlement Endpoint."""

    @patch("requests.Session")
    def test_endpoint(self, mock_session):
        """Testing endpoint."""

        mock_merchant_api = MagicMock()
        mock_merchant_api.status_code = 200
        mock_merchant_api.json.return_value ={
                "count": "2",
                "next": None,
                "prevous": None,
                "results": [
                    {
                        "id": "98f9d65c-6dd8-46a9-8850-f5afd9a49013",
                        "created_at": "2022-12-11T03:51:31Z",
                        "updated_at": "2022-12-11T03:51:31Z",
                        "name": "Some Name"
                    },
                    {
                        "id": "some_uuid",
                        "created_at": "2022-12-11T03:51:31Z",
                        "updated_at": "2022-12-11T03:51:31Z",
                        "name": "some_merchant"
                    }
                ]

        }

        mock_transaction_api = MagicMock()
        mock_transaction_api.status_code = 200
        mock_transaction_api.json.return_value ={
                "count": "2",
                "next": None,
                "prevous": None,
                "results": [
                    {
                        "id": "778b798b-3fbc-4f9f-8625-c9bb08b12e6f",
                        "created_at": "2023-01-13T02:11:17Z",
                        "updated_at": "2023-01-13T02:11:17Z",
                        "amount": "250.00",
                        "type": "REFUND",
                        "customer": "6141b6ad-6375-449b-be14-123958d26797",
                        "merchant": "some_merchant",
                        "order": "2673bb89-e18a-4cde-b4cd-26c0f031c3fa"
                    },
                    {
                        "id": "778b798b-3fbc-4f9f-8625-c9bb08b12e6g",
                        "created_at": "2023-01-13T02:11:17Z",
                        "updated_at": "2023-01-13T02:11:17Z",
                        "amount": "500.00",
                        "type": "REFUND",
                        "customer": "6141b6ad-6375-449b-be14-123958d2679g",
                        "merchant": "some_merchant",
                        "order": "2673bb89-e18a-4cde-b4cd-26c0f031c3fb"
                    }
                ]

        }        
        mock_session.return_value.get.side_effect = [mock_merchant_api, mock_transaction_api]

        client = TestClient(app)
        response = client.post(
                "/settlement",
                json = {
                    "merchant": "some_merchant",
                    "closing_date": "2024-02-12"
                }
        )

        assert response.status_code == 200
        response_json = response.json()
        assert response_json['amount'] == -750

    @patch("requests.Session")
    def test_endpoint_no_merchant(self, mock_session):
        """Testing endpoint."""

        mock_merchant_api = MagicMock()
        mock_merchant_api.status_code = 200
        mock_merchant_api.json.return_value ={
                "count": "2",
                "next": None,
                "prevous": None,
                "results": [
                    {
                        "id": "98f9d65c-6dd8-46a9-8850-f5afd9a49013",
                        "created_at": "2022-12-11T03:51:31Z",
                        "updated_at": "2022-12-11T03:51:31Z",
                        "name": "Some Name"
                    },
                    {
                        "id": "some_uuid",
                        "created_at": "2022-12-11T03:51:31Z",
                        "updated_at": "2022-12-11T03:51:31Z",
                        "name": "some_merchant"
                    }
                ]

        }

        mock_session.return_value.get.side_effect = [mock_merchant_api]

        client = TestClient(app)
        response = client.post(
                "/settlement",
                json = {
                    "merchant": "xx",
                    "closing_date": "2024-02-12"
                }
        )

        assert response.status_code == 404
        response_json = response.json()
        assert response_json['detail'] == 'xx not found in system'
