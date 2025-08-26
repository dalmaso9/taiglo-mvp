import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { 
  MapPin, Star, Phone, Globe, Instagram, Clock, DollarSign, 
  ArrowLeft, Coffee, Utensils, TreePine, Palette, ThumbsUp,
  Calendar, User, MessageSquare, Send
} from 'lucide-react'

const API_BASE_URL = 'http://localhost:3000/api'

export default function ExperienceDetails() {
  const { id } = useParams()
  const { user } = useAuth()
  const [experience, setExperience] = useState(null)
  const [reviews, setReviews] = useState([])
  const [reviewStats, setReviewStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [reviewLoading, setReviewLoading] = useState(false)
  const [newReview, setNewReview] = useState({
    rating: '',
    title: '',
    content: '',
    visit_date: ''
  })

  useEffect(() => {
    fetchExperienceDetails()
  }, [id])

  const fetchExperienceDetails = async () => {
    try {
      setLoading(true)
      const response = await fetch(`${API_BASE_URL}/experiences/${id}/full`)
      if (response.ok) {
        const data = await response.json()
        setExperience(data.experience)
        setReviews(data.reviews || [])
        setReviewStats(data.review_stats || {})
      }
    } catch (error) {
      console.error('Erro ao buscar detalhes da experiência:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleReviewSubmit = async (e) => {
    e.preventDefault()
    if (!newReview.rating || !newReview.content) return

    try {
      setReviewLoading(true)
      const token = localStorage.getItem('taiglo_token')
      const response = await fetch(`${API_BASE_URL}/reviews`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          experience_id: id,
          user_id: user.id,
          rating: parseInt(newReview.rating),
          title: newReview.title,
          content: newReview.content,
          visit_date: newReview.visit_date || null
        })
      })

      if (response.ok) {
        setNewReview({ rating: '', title: '', content: '', visit_date: '' })
        fetchExperienceDetails() // Recarregar dados
      }
    } catch (error) {
      console.error('Erro ao criar avaliação:', error)
    } finally {
      setReviewLoading(false)
    }
  }

  const getCategoryIcon = (categoryName) => {
    const icons = {
      'Cafés': Coffee,
      'Restaurantes': Utensils,
      'Parques': TreePine,
      'Arte': Palette,
      'Museus': Palette
    }
    return icons[categoryName] || MapPin
  }

  const formatOpeningHours = (hours) => {
    if (!hours || Object.keys(hours).length === 0) return null
    return Object.entries(hours).map(([day, time]) => (
      <div key={day} className="flex justify-between">
        <span className="capitalize">{day}:</span>
        <span>{time}</span>
      </div>
    ))
  }

  const renderStars = (rating) => {
    return [...Array(5)].map((_, i) => (
      <Star
        key={i}
        className={`h-4 w-4 ${
          i < rating ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'
        }`}
      />
    ))
  }

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-gray-200 rounded w-1/4"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
          <div className="h-6 bg-gray-200 rounded w-1/2"></div>
          <div className="h-4 bg-gray-200 rounded"></div>
          <div className="h-4 bg-gray-200 rounded w-3/4"></div>
        </div>
      </div>
    )
  }

  if (!experience) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Card>
          <CardContent className="pt-6 text-center">
            <MapPin className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Experiência não encontrada
            </h3>
            <p className="text-gray-600 mb-4">
              A experiência que você está procurando não existe ou foi removida.
            </p>
            <Link to="/">
              <Button>
                <ArrowLeft className="h-4 w-4 mr-2" />
                Voltar ao início
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    )
  }

  const CategoryIcon = getCategoryIcon(experience.category?.name)
  const userHasReviewed = reviews.some(review => review.user_id === user?.id)

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Back Button */}
      <div className="mb-6">
        <Link to="/">
          <Button variant="ghost" className="pl-0">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Voltar
          </Button>
        </Link>
      </div>

      {/* Main Experience Card */}
      <Card className="mb-8">
        <div className="relative">
          <div className="h-64 bg-gradient-to-br from-blue-100 to-purple-100 rounded-t-lg flex items-center justify-center">
            <CategoryIcon className="h-24 w-24 text-gray-400" />
          </div>
          {experience.is_hidden_gem && (
            <Badge className="absolute top-4 right-4 bg-amber-500 text-white">
              💎 Hidden Gem
            </Badge>
          )}
        </div>

        <CardContent className="pt-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                {experience.name}
              </h1>
              {experience.category && (
                <Badge variant="secondary" className="mb-2">
                  {experience.category.name}
                </Badge>
              )}
            </div>
            
            {experience.average_rating > 0 && (
              <div className="text-right">
                <div className="flex items-center space-x-1 mb-1">
                  {renderStars(Math.round(experience.average_rating))}
                </div>
                <div className="text-2xl font-bold text-gray-900">
                  {experience.average_rating.toFixed(1)}
                </div>
                <div className="text-sm text-gray-600">
                  {experience.total_reviews} avaliações
                </div>
              </div>
            )}
          </div>

          <p className="text-gray-700 text-lg mb-6">
            {experience.description}
          </p>

          {/* Photos Section */}
          {experience.photos && experience.photos.length > 0 && (
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Fotos</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {experience.photos.map((photo, index) => (
                  <div key={index} className="relative group">
                    <img
                      src={photo}
                      alt={`Foto ${index + 1} de ${experience.name}`}
                      className="w-full h-48 object-cover rounded-lg shadow-md hover:shadow-lg transition-shadow duration-200"
                    />
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Contact Info */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <MapPin className="h-5 w-5 text-gray-500" />
                <span className="text-gray-700">{experience.address}</span>
              </div>
              
              {experience.phone && (
                <div className="flex items-center space-x-2">
                  <Phone className="h-5 w-5 text-gray-500" />
                  <span className="text-gray-700">{experience.phone}</span>
                </div>
              )}
              
              {experience.website_url && (
                <div className="flex items-center space-x-2">
                  <Globe className="h-5 w-5 text-gray-500" />
                  <a 
                    href={experience.website_url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-primary hover:underline"
                  >
                    Website
                  </a>
                </div>
              )}
              
              {experience.instagram_handle && (
                <div className="flex items-center space-x-2">
                  <Instagram className="h-5 w-5 text-gray-500" />
                  <a 
                    href={`https://instagram.com/${experience.instagram_handle.replace('@', '')}`}
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-primary hover:underline"
                  >
                    {experience.instagram_handle}
                  </a>
                </div>
              )}
            </div>

            <div className="space-y-3">
              {experience.opening_hours && Object.keys(experience.opening_hours).length > 0 && (
                <div>
                  <div className="flex items-center space-x-2 mb-2">
                    <Clock className="h-5 w-5 text-gray-500" />
                    <span className="font-medium text-gray-700">Horário de funcionamento</span>
                  </div>
                  <div className="text-sm text-gray-600 space-y-1 ml-7">
                    {formatOpeningHours(experience.opening_hours)}
                  </div>
                </div>
              )}
              
              {experience.price_range && (
                <div className="flex items-center space-x-2">
                  <DollarSign className="h-5 w-5 text-gray-500" />
                  <span className="text-gray-700">
                    Faixa de preço: {'$'.repeat(experience.price_range)}
                  </span>
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Review Stats */}
      {reviewStats && reviewStats.total_reviews > 0 && (
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Estatísticas das Avaliações</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              {Object.entries(reviewStats.rating_distribution).map(([rating, count]) => (
                <div key={rating} className="text-center">
                  <div className="flex items-center justify-center space-x-1 mb-1">
                    <span className="text-sm">{rating}</span>
                    <Star className="h-3 w-3 fill-yellow-400 text-yellow-400" />
                  </div>
                  <div className="text-2xl font-bold text-gray-900">{count}</div>
                  <div className="text-xs text-gray-600">avaliações</div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Add Review */}
      {user && !userHasReviewed && (
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Avalie esta experiência</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleReviewSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Avaliação *
                  </label>
                  <Select value={newReview.rating} onValueChange={(value) => setNewReview({...newReview, rating: value})}>
                    <SelectTrigger>
                      <SelectValue placeholder="Selecione uma nota" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="5">⭐⭐⭐⭐⭐ Excelente</SelectItem>
                      <SelectItem value="4">⭐⭐⭐⭐ Muito bom</SelectItem>
                      <SelectItem value="3">⭐⭐⭐ Bom</SelectItem>
                      <SelectItem value="2">⭐⭐ Regular</SelectItem>
                      <SelectItem value="1">⭐ Ruim</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Data da visita
                  </label>
                  <input
                    type="date"
                    value={newReview.visit_date}
                    onChange={(e) => setNewReview({...newReview, visit_date: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Título da avaliação
                </label>
                <input
                  type="text"
                  placeholder="Ex: Experiência incrível!"
                  value={newReview.title}
                  onChange={(e) => setNewReview({...newReview, title: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Sua avaliação *
                </label>
                <Textarea
                  placeholder="Conte sobre sua experiência neste lugar..."
                  value={newReview.content}
                  onChange={(e) => setNewReview({...newReview, content: e.target.value})}
                  rows={4}
                  required
                />
              </div>
              
              <Button type="submit" disabled={reviewLoading || !newReview.rating || !newReview.content}>
                {reviewLoading ? (
                  <>Enviando...</>
                ) : (
                  <>
                    <Send className="h-4 w-4 mr-2" />
                    Enviar Avaliação
                  </>
                )}
              </Button>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Reviews */}
      {reviews.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Avaliações ({reviews.length})</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {reviews.map((review) => (
              <div key={review.id} className="border-b border-gray-200 last:border-b-0 pb-6 last:pb-0">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center space-x-3">
                    <div className="bg-primary/10 rounded-full p-2">
                      <User className="h-4 w-4 text-primary" />
                    </div>
                    <div>
                      <div className="font-medium text-gray-900">
                        {review.user?.first_name} {review.user?.last_name}
                      </div>
                      <div className="flex items-center space-x-2 text-sm text-gray-600">
                        <div className="flex items-center space-x-1">
                          {renderStars(review.rating)}
                        </div>
                        {review.visit_date && (
                          <>
                            <span>•</span>
                            <div className="flex items-center space-x-1">
                              <Calendar className="h-3 w-3" />
                              <span>{new Date(review.visit_date).toLocaleDateString('pt-BR')}</span>
                            </div>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  {review.helpful_votes > 0 && (
                    <div className="flex items-center space-x-1 text-sm text-gray-600">
                      <ThumbsUp className="h-3 w-3" />
                      <span>{review.helpful_votes}</span>
                    </div>
                  )}
                </div>
                
                {review.title && (
                  <h4 className="font-semibold text-gray-900 mb-2">
                    {review.title}
                  </h4>
                )}
                
                <p className="text-gray-700 mb-3">
                  {review.content}
                </p>
                
                <div className="text-xs text-gray-500">
                  {new Date(review.created_at).toLocaleDateString('pt-BR')}
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  )
}

