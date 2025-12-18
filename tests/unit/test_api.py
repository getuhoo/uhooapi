import pytest
import aioresponses
from unittest.mock import AsyncMock, MagicMock, Mock, patch
from aiohttp import ClientResponseError, ClientError
from uhooapi.api import API
from uhooapi.errors import UnauthorizedError, ForbiddenError, RequestError


class TestAPIInitialization:
    """Test API class initialization."""
    
    @pytest.mark.asyncio
    async def test_api_init(self, mock_websession):
        """Test API initialization."""
        api = API(mock_websession)
        
        assert api._websession == mock_websession
        assert api._bearer_token is None
        assert api._log is not None


class TestAPIRequest:
    """Test API _request method."""
    
    @pytest.mark.asyncio
    async def test_request_success_json(self, mock_websession):
        """Test successful JSON request."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.content_type = "application/json"
        mock_response.json = AsyncMock(return_value={"success": True})
        mock_response.raise_for_status = MagicMock()
        mock_response.text = AsyncMock(return_value='{"success": true}')

        #Mock the async context manager protocol
        mock_context_manager = AsyncMock()
        mock_context_manager.__aenter__ = AsyncMock(return_value=mock_response)
        mock_context_manager.__aexit__ = AsyncMock(return_value=None)
        
        mock_websession.request.return_value = mock_context_manager
        
        api = API(mock_websession)
        result = await api._request("GET", "https://api.example.com", "test")
        
        assert result == {"success": True}
        mock_websession.request.assert_called_once_with(
            "GET", "https://api.example.com/test", headers={}, data=None
        )
    
    @pytest.mark.asyncio
    async def test_request_with_bearer_token(self, mock_websession):
        """Test request with bearer token."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.content_type = "application/json"
        mock_response.json = AsyncMock(return_value={"success": True})
        mock_response.raise_for_status = MagicMock()
        
        mock_context_manager = AsyncMock()
        mock_context_manager.__aenter__ = AsyncMock(return_value=mock_response)
        mock_context_manager.__aexit__ = AsyncMock(return_value=None)
        
        mock_websession.request.return_value = mock_context_manager
        
        api = API(mock_websession)
        api.set_bearer_token("test-token")
        result = await api._request("GET", "https://api.example.com", "test")
        
        mock_websession.request.assert_called_once_with(
            "GET", "https://api.example.com/test",
            headers={"Authorization": "Bearer test-token"},
            data=None
        )
    
    @pytest.mark.asyncio
    async def test_request_with_data(self, mock_websession):
        """Test request with POST data."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.content_type = "application/json"
        mock_response.json = AsyncMock(return_value={"success": True})
        mock_response.raise_for_status = MagicMock()
        
        mock_context_manager = AsyncMock()
        mock_context_manager.__aenter__ = AsyncMock(return_value=mock_response)
        mock_context_manager.__aexit__ = AsyncMock(return_value=None)
        
        mock_websession.request.return_value = mock_context_manager
        
        api = API(mock_websession)
        data = {"test": "data"}
        result = await api._request("POST", "https://api.example.com", "test", data=data)
        
        mock_websession.request.assert_called_once_with(
            "POST", "https://api.example.com/test",
            headers={}, data={"test": "data"}
        )
    
    @pytest.mark.asyncio
    async def test_request_unauthorized(self, mock_websession):
        """Test request with 401 Unauthorized."""
        mock_response = AsyncMock()
        mock_response.status = 401
        mock_response.content_type = "application/json"
        mock_response.json = AsyncMock(return_value={"error": "Unauthorized"})
        mock_response.raise_for_status = MagicMock(side_effect=ClientResponseError(
            request_info=None, history=None, status=401, message="Unauthorized"
        ))
        mock_response.text = AsyncMock(return_value='{"error": "Unauthorized"}')
        
        mock_context_manager = AsyncMock()
        mock_context_manager.__aenter__ = AsyncMock(return_value=mock_response)
        mock_context_manager.__aexit__ = AsyncMock(return_value=None)
        
        mock_websession.request.return_value = mock_context_manager
        
        api = API(mock_websession)
        
        with pytest.raises(UnauthorizedError):
            await api._request("GET", "https://api.example.com", "test")
    
    @pytest.mark.asyncio
    async def test_request_forbidden(self, mock_websession):
        """Test request with 403 Forbidden."""
        mock_response = AsyncMock()
        mock_response.status = 403
        mock_response.content_type = "text/plain"
        mock_response.text = AsyncMock(return_value="Forbidden")
        mock_response.raise_for_status = MagicMock(side_effect=ClientResponseError(
            request_info=None, history=None, status=403, message="Forbidden"
        ))
        
        mock_context_manager = AsyncMock()
        mock_context_manager.__aenter__ = AsyncMock(return_value=mock_response)
        mock_context_manager.__aexit__ = AsyncMock(return_value=None)
        
        mock_websession.request.return_value = mock_context_manager
        
        api = API(mock_websession)
        
        with pytest.raises(ForbiddenError):
            await api._request("GET", "https://api.example.com", "test")
    

    @pytest.mark.asyncio
    async def test_request_other_error(self, mock_websession):
        """Test request with other HTTP error."""
        # Import here to avoid circular imports
        from aiohttp.client import RequestInfo
        
        # Create a proper RequestInfo mock
        mock_request_info = Mock(spec=RequestInfo)
        mock_request_info.real_url = "https://api.example.com/test"
        
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_response.content_type = "application/json"
        mock_response.json = AsyncMock(return_value={"error": "Server Error"})
        
        # Create the ClientResponseError properly
        client_response_error = ClientResponseError(
            mock_request_info,
            (),
            status=500,
            message="Server Error"
        )
        mock_response.raise_for_status = MagicMock(side_effect=client_response_error)
        
        mock_websession.request.return_value.__aenter__ = AsyncMock(return_value=mock_response)
        mock_websession.request.return_value.__aexit__ = AsyncMock(return_value=None)
        
        api = API(mock_websession)
        
        with pytest.raises(RequestError, match="Error requesting data"):
            await api._request("GET", "https://api.example.com", "test")
    
    @pytest.mark.asyncio
    async def test_request_client_error(self, mock_websession):
        """Test request with client error (e.g., network issue)."""
        # Create a mock response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.content_type = "application/json"
        # Make json() raise ClientError
        mock_response.json = AsyncMock(side_effect=ClientError("Network error"))
        mock_response.raise_for_status = AsyncMock()  # This won't be reached
        mock_response.text = AsyncMock(return_value="")
        
        # Create a context manager
        mock_context_manager = AsyncMock()
        mock_context_manager.__aenter__ = AsyncMock(return_value=mock_response)
        mock_context_manager.__aexit__ = AsyncMock(return_value=None)
        
        mock_websession.request.return_value = mock_context_manager
        
        api = API(mock_websession)
        
        with pytest.raises(RequestError, match="Error requesting data"):
            await api._request("GET", "https://api.example.com", "test")


class TestAPIMethods:
    """Test API public methods."""
    
    @pytest.mark.asyncio
    async def test_generate_token(self, mock_websession):
        """Test generate_token method."""
        mock_response = {"access_token": "test-token"}
        
        with patch.object(API, '_request', AsyncMock(return_value=mock_response)) as mock_request:
            api = API(mock_websession)
            result = await api.generate_token("test-code")
            
            mock_request.assert_called_once_with(
                "post", "https://api.uhooinc.com/integration", "generatetoken",
                data={"code": "test-code"}
            )
            assert result == mock_response
    
    @pytest.mark.asyncio
    async def test_get_device_data(self, mock_websession):
        """Test get_device_data method."""
        mock_response = {"data": []}
        
        with patch.object(API, '_request', AsyncMock(return_value=mock_response)) as mock_request:
            api = API(mock_websession)
            result = await api.get_device_data("UHOO12345", "minute", 5)
            
            mock_request.assert_called_once_with(
                "post", "https://api.uhooinc.com/integration", "getdata",
                data={"serialNumber": "UHOO12345", "mode": "minute", "limit": 5}
            )
            assert result == mock_response
    
    @pytest.mark.asyncio
    async def test_get_device_list(self, mock_websession):
        """Test get_device_list method."""
        mock_response = []
        
        with patch.object(API, '_request', AsyncMock(return_value=mock_response)) as mock_request:
            api = API(mock_websession)
            result = await api.get_device_list()
            
            mock_request.assert_called_once_with(
                "post", "https://api.uhooinc.com/integration", "getdeviceslist"
            )
            assert result == mock_response
    
    def test_set_bearer_token(self, mock_websession):
        """Test set_bearer_token method."""
        api = API(mock_websession)
        assert api._bearer_token is None
        
        api.set_bearer_token("test-token")
        assert api._bearer_token == "test-token"
        
        api.set_bearer_token(None)
        assert api._bearer_token is None